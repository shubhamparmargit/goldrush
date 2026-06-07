from django.db import models
from customer.models import Customer
from customer_wallet.models import CustomerWallet, MembershipMaster, CustomerDemoWallet

TRANSACTION_TYPE = (
    ("BUY", "Buy"),
    ("SELL", "Sell"),
)

METAL_TYPE = (
    ("GOLD", "Gold"),
    ("SILVER", "Silver"),
)

PNL_TYPE = (
    ("PROFIT", "Profit"),
    ("LOSS", "Loss"),
)

ORDER_TYPE = (
    ("BOOKING", "Booking"),
    ("BUYBACK", "Buyback"),
)

SOLD_VIA_CHOICES = (
    ("MANUAL", "Manual"),
    ("AUTO", "Auto Sell"),
)

class CustomerTransaction(models.Model):
    class Meta:
        db_table = "customer_transaction"
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]

    transaction_id = models.CharField(max_length=32, unique=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    wallet = models.ForeignKey(CustomerWallet, on_delete=models.CASCADE)
    membership = models.ForeignKey(MembershipMaster, on_delete=models.PROTECT)

    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE)
    metal_type = models.CharField(max_length=6, choices=METAL_TYPE, default="GOLD")
    order_type = models.CharField(max_length=10,choices=ORDER_TYPE, default="BOOKING")

    quantity_gm = models.PositiveIntegerField()

    metal_rate_per_gm = models.DecimalField(max_digits=10, decimal_places=2)
    metal_value = models.DecimalField(max_digits=14, decimal_places=2)   # optional but recommended
    currency = models.CharField(max_length=3, default="INR")

    order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=10, decimal_places=2)
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    actual_service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    market_amount = models.DecimalField(max_digits=12, decimal_places=2)

    parent_buy = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,related_name="sell_transactions")

    created_at = models.DateTimeField(auto_now_add=True)

    profit_loss = models.CharField(max_length=6, choices=PNL_TYPE, null=True, blank=True)
    profit_loss_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    profit_loss_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    auto_sell_enabled = models.BooleanField(default=False)
    auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Auto sell trigger value set by user")
    sold_via = models.CharField(max_length=10, choices=SOLD_VIA_CHOICES, default="MANUAL")

class TransactionAutoSellHistory(models.Model):
    class Meta:
        db_table = "transaction_auto_sell_history"
        ordering = ["-created_at"]

    transaction = models.ForeignKey(CustomerTransaction, on_delete=models.CASCADE, related_name="auto_sell_history")
    old_auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.CharField(max_length=20, default="CUSTOMER", help_text="CUSTOMER / SYSTEM")
    created_at = models.DateTimeField(auto_now_add=True)

class CustomerDemoTransaction(models.Model):
    class Meta:
        db_table = "customer_demo_transaction"
        indexes = [
            models.Index(fields=['customer', 'created_at']),
        ]

    transaction_id = models.CharField(max_length=32, unique=True)

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    wallet = models.ForeignKey(CustomerDemoWallet, on_delete=models.CASCADE)
    membership = models.ForeignKey(MembershipMaster, on_delete=models.SET_NULL, null=True)

    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPE)
    metal_type = models.CharField(max_length=6, choices=METAL_TYPE, default="GOLD")
    order_type = models.CharField(max_length=10,choices=ORDER_TYPE, default="BOOKING")

    quantity_gm = models.PositiveIntegerField()

    metal_rate_per_gm = models.DecimalField(max_digits=10, decimal_places=2)
    metal_value = models.DecimalField(max_digits=14, decimal_places=2)   # optional but recommended
    currency = models.CharField(max_length=3, default="INR")

    order_amount = models.DecimalField(max_digits=12, decimal_places=2)
    service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    gst = models.DecimalField(max_digits=10, decimal_places=2)
    reward = models.DecimalField(max_digits=10, decimal_places=2)
    actual_service_fee = models.DecimalField(max_digits=10, decimal_places=2)
    market_amount = models.DecimalField(max_digits=12, decimal_places=2)

    parent_buy = models.ForeignKey("self",on_delete=models.SET_NULL,null=True,blank=True,related_name="demo_sell_transactions")

    created_at = models.DateTimeField(auto_now_add=True)

    profit_loss = models.CharField(max_length=6, choices=PNL_TYPE, null=True, blank=True)
    profit_loss_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    profit_loss_percent = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    auto_sell_enabled = models.BooleanField(default=False)
    auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Auto sell trigger value set by user")
    sold_via = models.CharField(max_length=10, choices=SOLD_VIA_CHOICES, default="MANUAL")

class DemoTransactionAutoSellHistory(models.Model):
    class Meta:
        db_table = "demo_transaction_auto_sell_history"
        ordering = ["-created_at"]

    transaction = models.ForeignKey(CustomerDemoTransaction, on_delete=models.CASCADE, related_name="demo_auto_sell_history")
    old_auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    new_auto_sell_amount = models.DecimalField(max_digits=12, decimal_places=2)
    changed_by = models.CharField(max_length=20, default="CUSTOMER", help_text="CUSTOMER / SYSTEM")
    created_at = models.DateTimeField(auto_now_add=True)