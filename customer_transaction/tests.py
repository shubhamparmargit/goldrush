from django.test import TestCase
from django.core.management import call_command
from unittest.mock import patch
from decimal import Decimal
from django.utils import timezone
from customer.models import Customer
from customer_wallet.models import MembershipMaster, CustomerWallet, CustomerDemoWallet
from customer_transaction.models import CustomerTransaction, CustomerDemoTransaction
from customer_transaction.views import OrderList, get_active_live_orders
from utility.views import RandomIdGenerate

random_obj = RandomIdGenerate()

class WeeklyAutoCloseTestCase(TestCase):
    def setUp(self):
        # 1. Create a customer
        self.customer = Customer.objects.create(
            unique_id="12345678",
            name="Test Customer",
            mobile="9876543210",
            email="test@example.com",
            access="Granted",
            trading="ON",
            date=timezone.now()
        )
        
        # 2. Create a membership level
        self.membership = MembershipMaster.objects.create(
            level="Normal",
            min_amount=Decimal("0"),
            service_fee=Decimal("50"),  # service fee per 10gm
            service_fee_percent=Decimal("0.10"),
            daily_slot=100
        )
        
        # 3. Create live and demo wallets
        self.wallet_live = CustomerWallet.objects.create(
            customer=self.customer,
            balance=Decimal("10000.00"),
            current_membership=self.membership
        )
        self.wallet_demo = CustomerDemoWallet.objects.create(
            customer=self.customer,
            balance=Decimal("10000.00"),
            current_membership=self.membership
        )

        # 4. Mock rates to return standard values
        self.mock_rates = {
            "buy_gold_rate": Decimal("6000.0"),
            "sell_gold_rate": Decimal("5900.0"),
            "buy_silver_rate": Decimal("75.0"),
            "sell_silver_rate": Decimal("70.0"),
            "spread": Decimal("200"),
            "currency": "INR",
            "currency_icon": "₹"
        }

    @patch("customer_transaction.services.getMetalRate")
    def test_weekly_auto_close_workflow(self, mock_get_metal_rate):
        mock_get_metal_rate.return_value = self.mock_rates

        # Create active live BUY transaction (Gold booking)
        # Order amount = 10gm * 50 = 500
        # Service fee = 50 - 0 = 50
        # Actual service fee = 50 - (9 + 5) = 36
        # Market amount = 450
        # Invested amount = 500
        live_buy = CustomerTransaction.objects.create(
            transaction_id="TXN_LIVE_BUY_1",
            customer=self.customer,
            wallet=self.wallet_live,
            membership=self.membership,
            transaction_type="BUY",
            metal_type="GOLD",
            order_type="BOOKING",
            quantity_gm=10,
            metal_rate_per_gm=Decimal("6000.0"),
            metal_value=Decimal("6000.0"),
            order_amount=Decimal("500.0"),
            service_fee=Decimal("50.0"),
            gst=Decimal("9.0"),
            reward=Decimal("5.0"),
            actual_service_fee=Decimal("36.0"),
            market_amount=Decimal("450.0"),
            created_at=timezone.now()
        )

        # Create active demo BUY transaction
        demo_buy = CustomerDemoTransaction.objects.create(
            transaction_id="TXN_DEMO_BUY_1",
            customer=self.customer,
            wallet=self.wallet_demo,
            membership=self.membership,
            transaction_type="BUY",
            metal_type="GOLD",
            order_type="BOOKING",
            quantity_gm=10,
            metal_rate_per_gm=Decimal("6000.0"),
            metal_value=Decimal("6000.0"),
            order_amount=Decimal("500.0"),
            service_fee=Decimal("50.0"),
            gst=Decimal("9.0"),
            reward=Decimal("5.0"),
            actual_service_fee=Decimal("36.0"),
            market_amount=Decimal("450.0"),
            created_at=timezone.now()
        )

        # Wallet balance subtraction matches buying:
        self.wallet_live.balance -= Decimal("500.0")
        self.wallet_live.save()
        self.wallet_demo.balance -= Decimal("500.0")
        self.wallet_demo.save()

        # Verify orders are in active state before run
        # We need a mock request for helper functions
        class MockRequest:
            is_demo_account = False
            
        class MockRequestDemo:
            is_demo_account = True

        self.assertEqual(get_active_live_orders(MockRequest(), self.customer).count(), 1)
        self.assertEqual(get_active_live_orders(MockRequestDemo(), self.customer).count(), 1)

        # Call the management command to run weekly close
        call_command("close_weekly_orders")

        # Refresh from database
        live_buy.refresh_from_db()
        demo_buy.refresh_from_db()
        self.wallet_live.refresh_from_db()
        self.wallet_demo.refresh_from_db()

        # Assert BUY transactions are updated
        self.assertTrue(live_buy.auto_closed_weekly)
        self.assertFalse(live_buy.auto_sell_enabled)
        self.assertTrue(demo_buy.auto_closed_weekly)
        self.assertFalse(demo_buy.auto_sell_enabled)

        # Assert SELL transactions are created
        live_sell = CustomerTransaction.objects.get(parent_buy=live_buy)
        demo_sell = CustomerDemoTransaction.objects.get(parent_buy=demo_buy)

        self.assertEqual(live_sell.transaction_type, "SELL")
        self.assertEqual(live_sell.sold_via, "WEEKLY_AUTO_CLOSE")
        self.assertTrue(live_sell.auto_closed_weekly)

        self.assertEqual(demo_sell.transaction_type, "SELL")
        self.assertEqual(demo_sell.sold_via, "WEEKLY_AUTO_CLOSE")
        self.assertTrue(demo_sell.auto_closed_weekly)

        # Check PnL calculations
        # buy rate: 6000, current sell rate (gold): 5900
        # quantity: 10gm
        # booking order direction: PnL = (sell_rate - buy_rate) * quantity = (5900 - 6000) * 10 = -1000 (Loss)
        # market amount: 450
        # current value: 450 + (-1000) = -550. Under execute_sell, current_value < 0 gets set to 0.0, and loss becomes -450 (100% loss).
        # live_sell.order_amount should be 0.0, and wallet gets credited with 0.0.
        # Let's verify wallet balance: original 10000 - 500 (buy) + 0.0 (sell) = 9500.0
        self.assertEqual(self.wallet_live.balance, Decimal("9500.00"))
        self.assertEqual(live_sell.profit_loss, "LOSS")
        self.assertEqual(live_sell.profit_loss_amount, Decimal("-450.00"))

        # Verify customer side hides these orders
        # 1. Active orders should be 0
        self.assertEqual(get_active_live_orders(MockRequest(), self.customer).count(), 0)
        self.assertEqual(get_active_live_orders(MockRequestDemo(), self.customer).count(), 0)

        # 2. Past orders should also be 0 (hidden)
        order_list = OrderList()
        past_live = order_list.get_past_orders(MockRequest(), self.customer)
        past_demo = order_list.get_past_orders(MockRequestDemo(), self.customer)
        self.assertEqual(len(past_live), 0)
        self.assertEqual(len(past_demo), 0)

class AutoSellTestCase(TestCase):
    def setUp(self):
        # Create customer, membership level, wallets, mock rates
        self.customer = Customer.objects.create(
            unique_id="12345678_auto",
            name="Auto Sell Customer",
            mobile="9876543211",
            email="autosell@example.com",
            access="Granted",
            trading="ON",
            date=timezone.now()
        )
        self.membership = MembershipMaster.objects.create(
            level="Normal",
            min_amount=Decimal("0"),
            service_fee=Decimal("50"),
            service_fee_percent=Decimal("0.10"),
            daily_slot=100
        )
        self.wallet_live = CustomerWallet.objects.create(
            customer=self.customer,
            balance=Decimal("10000.00"),
            current_membership=self.membership,
            stop_loss_percentage=80  # 80% stop loss
        )

    @patch("customer_transaction.services.getMetalRate")
    def test_auto_sell_profit_target_triggered(self, mock_get_metal_rate):
        # Initial rates at 6000.0, but we will mock it to 6010.0 to trigger profit target
        mock_get_metal_rate.return_value = {
            "buy_gold_rate": Decimal("6010.0"),
            "sell_gold_rate": Decimal("6010.0"),
            "buy_silver_rate": Decimal("75.0"),
            "sell_silver_rate": Decimal("75.0"),
            "spread": Decimal("0"),
            "currency": "INR",
            "currency_icon": "₹"
        }

        # Create active BUY order with profit target auto_sell_amount = 500 INR
        # order_amount = 500, service_fee = 50, market_amount = 450
        # If rate goes up to 6010, current_value = 450 + 10*(6010-6000) = 550, which >= 500
        order = CustomerTransaction.objects.create(
            transaction_id="TXN_AUTO_SELL_PROFIT",
            customer=self.customer,
            wallet=self.wallet_live,
            membership=self.membership,
            transaction_type="BUY",
            metal_type="GOLD",
            order_type="BOOKING",
            quantity_gm=10,
            metal_rate_per_gm=Decimal("6000.0"),
            metal_value=Decimal("6000.0"),
            order_amount=Decimal("500.0"),
            service_fee=Decimal("50.0"),
            gst=Decimal("9.0"),
            reward=Decimal("5.0"),
            actual_service_fee=Decimal("36.0"),
            market_amount=Decimal("450.0"),
            auto_sell_enabled=True,
            auto_sell_amount=Decimal("500.0"),
            created_at=timezone.now()
        )

        from customer_transaction.services import auto_sell_runner
        auto_sell_runner()

        # Check if the order was auto sold
        order.refresh_from_db()
        sell_txns = CustomerTransaction.objects.filter(parent_buy=order)
        self.assertEqual(sell_txns.count(), 1)
        sell_txn = sell_txns.first()
        self.assertEqual(sell_txn.transaction_type, "SELL")
        self.assertEqual(sell_txn.sold_via, "AUTO")

    @patch("customer_transaction.services.getMetalRate")
    def test_auto_sell_stop_loss_triggered(self, mock_get_metal_rate):
        # Mock rate is 5960.0 to trigger stop loss (current_value = 450 - 400 = 50 <= limit_value of 90)
        mock_get_metal_rate.return_value = {
            "buy_gold_rate": Decimal("5960.0"),
            "sell_gold_rate": Decimal("5960.0"),
            "buy_silver_rate": Decimal("75.0"),
            "sell_silver_rate": Decimal("75.0"),
            "spread": Decimal("0"),
            "currency": "INR",
            "currency_icon": "₹"
        }

        order = CustomerTransaction.objects.create(
            transaction_id="TXN_AUTO_SELL_SL",
            customer=self.customer,
            wallet=self.wallet_live,
            membership=self.membership,
            transaction_type="BUY",
            metal_type="GOLD",
            order_type="BOOKING",
            quantity_gm=10,
            metal_rate_per_gm=Decimal("6000.0"),
            metal_value=Decimal("6000.0"),
            order_amount=Decimal("500.0"),
            service_fee=Decimal("50.0"),
            gst=Decimal("9.0"),
            reward=Decimal("5.0"),
            actual_service_fee=Decimal("36.0"),
            market_amount=Decimal("450.0"),
            auto_sell_enabled=True,
            created_at=timezone.now()
        )

        from customer_transaction.services import auto_sell_runner
        auto_sell_runner()

        # Check if the order was auto sold due to stop loss
        order.refresh_from_db()
        sell_txns = CustomerTransaction.objects.filter(parent_buy=order)
        self.assertEqual(sell_txns.count(), 1)
        sell_txn = sell_txns.first()
        self.assertEqual(sell_txn.transaction_type, "SELL")
        self.assertEqual(sell_txn.sold_via, "AUTO")
