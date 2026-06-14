from customer_transaction.models import CustomerTransaction, CustomerDemoTransaction
from customer_wallet.models import CustomerWallet, CustomerDemoWallet
from customer_transaction.views import getMetalRate, calculate_live_pnl, execute_sell
from django.db import transaction
from utility.views import RandomIdGenerate, current_date
from decimal import Decimal, ROUND_HALF_UP
import logging
import os
from django.conf import settings
from django.utils import timezone

# Setup logger for weekly auto-close
log_dir = os.path.join(settings.BASE_DIR, 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, 'weekly_close.log')

weekly_logger = logging.getLogger('weekly_close')
weekly_logger.setLevel(logging.INFO)

# Avoid duplicate handlers
if not weekly_logger.handlers:
    handler = logging.FileHandler(log_file)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
    handler.setFormatter(formatter)
    weekly_logger.addHandler(handler)

random_obj = RandomIdGenerate()

def process_auto_sell_for_orders(is_demo, current_rates):
    trans_model = CustomerDemoTransaction if is_demo else CustomerTransaction
    wallet_model = CustomerDemoWallet if is_demo else CustomerWallet
    sell_relation = "demo_sell_transactions" if is_demo else "sell_transactions"

    # Fetch all open BUY orders (where no sell transaction has been linked yet)
    live_orders = trans_model.objects.filter(
        transaction_type="BUY",
        **{f"{sell_relation}__isnull": True}
    )

    for order in live_orders:
        if order.order_type == "BOOKING":
            current_rate = current_rates["sell_gold_rate"] if order.metal_type == 'GOLD' else current_rates["sell_silver_rate"]
        else:
            current_rate = current_rates["buy_gold_rate"] if order.metal_type == 'GOLD' else current_rates["buy_silver_rate"]
        
        # Calculate current PNL and value
        pnl = calculate_live_pnl(order, current_rate)
        current_value = pnl["current_value"]

        # Fetch stop loss limit (default is 80% if not configured/found)
        try:
            wallet = wallet_model.objects.get(customer=order.customer)
            stop_loss_percentage = wallet.stop_loss_percentage
            if stop_loss_percentage is None:
                stop_loss_percentage = 80
        except wallet_model.DoesNotExist:
            stop_loss_percentage = 80

        # Create a mock request to pass the is_demo flag to execute_sell
        class MockRequest:
            is_demo_account = is_demo

        # 1. Check stop loss (close position if loss meets or exceeds stop_loss_percentage)
        # Note: stop_loss_percentage = 0 means disabled
        if stop_loss_percentage > 0:
            # Stop loss based on market_amount (order_amount minus service fee)
            # e.g. market_amount = ₹450, stop_loss = 80% → trigger when loss ≥ ₹360 → current_value ≤ ₹90
            limit_value = Decimal(order.market_amount) * (Decimal("1") - (Decimal(str(stop_loss_percentage)) / Decimal("100")))
            if current_value <= limit_value:
                execute_sell(
                    request=MockRequest(),
                    buy_txn=order,
                    current_metal_rate=current_rate,
                    sold_via="AUTO"
                )
                continue

        # 2. Check auto sell (profit target limit)
        if order.auto_sell_enabled and order.auto_sell_amount and current_value >= order.auto_sell_amount:
            execute_sell(
                request=MockRequest(),
                buy_txn=order,
                current_metal_rate=current_rate,
                sold_via="AUTO"
            )

def auto_sell_runner():
    try:
        current_rates = getMetalRate()
    except Exception:
        # If rates could not be fetched, abort
        return

    # Process live account orders
    process_auto_sell_for_orders(is_demo=False, current_rates=current_rates)
    
    # Process demo account orders
    process_auto_sell_for_orders(is_demo=True, current_rates=current_rates)


def process_weekly_close_for_orders(is_demo, current_rates):
    trans_model = CustomerDemoTransaction if is_demo else CustomerTransaction
    sell_relation = "demo_sell_transactions" if is_demo else "sell_transactions"

    # Fetch all open BUY orders (where no sell transaction has been linked yet)
    live_orders = trans_model.objects.filter(
        transaction_type="BUY",
        **{f"{sell_relation}__isnull": True}
    ).exclude(auto_closed_weekly=True)

    weekly_logger.info(f"Processing weekly auto-close for {live_orders.count()} open {'demo' if is_demo else 'live'} orders.")

    for order in live_orders:
        try:
            if order.order_type == "BOOKING":
                current_rate = current_rates["sell_gold_rate"] if order.metal_type == 'GOLD' else current_rates["sell_silver_rate"]
            else:
                current_rate = current_rates["buy_gold_rate"] if order.metal_type == 'GOLD' else current_rates["buy_silver_rate"]
            
            # Calculate current PNL and value
            pnl = calculate_live_pnl(order, current_rate)

            # Create a mock request to pass the is_demo flag to execute_sell
            class MockRequest:
                is_demo_account = is_demo

            weekly_logger.info(
                f"Closing order {order.transaction_id} (Customer ID: {order.customer.id}) "
                f"at rate {current_rate}."
            )

            result = execute_sell(
                request=MockRequest(),
                buy_txn=order,
                current_metal_rate=current_rate,
                sold_via="WEEKLY_AUTO_CLOSE"
            )

            if result:
                weekly_logger.info(
                    f"Successfully settled order {order.transaction_id}. "
                    f"PnL: {pnl['pnl_amount']} ({pnl['pnl_percent']}%). "
                    f"Wallet credited with settlement amount: {pnl['current_value']}. "
                    f"New wallet balance: {result['wallet_balance']}."
                )
            else:
                weekly_logger.warning(f"Order {order.transaction_id} could not be settled (returned None).")

        except Exception as e:
            weekly_logger.error(f"Error closing order {order.transaction_id}: {str(e)}")


def weekly_auto_close_runner():
    weekly_logger.info(f"Weekly auto-close runner triggered at {timezone.now()}")
    try:
        current_rates = getMetalRate()
        weekly_logger.info(f"Fetched live rates - Gold Buy: {current_rates['buy_gold_rate']}, Silver Buy: {current_rates['buy_silver_rate']}")
    except Exception as e:
        weekly_logger.error(f"Failed to fetch live metal rates: {str(e)}")
        return

    # Process live account orders
    process_weekly_close_for_orders(is_demo=False, current_rates=current_rates)
    
    # Process demo account orders
    process_weekly_close_for_orders(is_demo=True, current_rates=current_rates)
    
    weekly_logger.info("Weekly auto-close runner finished.")