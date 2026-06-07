from customer_transaction.models import CustomerTransaction
from customer_wallet.models import CustomerWallet
from customer_transaction.views import getMetalRate, calculate_live_pnl, execute_sell
from django.db import transaction
from utility.views import RandomIdGenerate, current_date
from decimal import Decimal, ROUND_HALF_UP

random_obj = RandomIdGenerate()

def auto_sell_runner():
    live_orders = CustomerTransaction.objects.filter(
        transaction_type="BUY",
        auto_sell_enabled=True,
        sell_transactions__isnull=True
    )

    current_rates = getMetalRate()   # once only

    for order in live_orders:
        current_rate = current_rates["sell_gold_rate"] if order.metal_type == 'GOLD' else current_rates["sell_silver_rate"]
        # current_rate = Decimal(158.04)

        pnl = calculate_live_pnl(order, current_rate)

        current_value = pnl["current_value"]

        if current_value >= order.auto_sell_amount:
            execute_sell(buy_txn=order,current_rate=current_rate,sold_via="AUTO")