from django.db import models
from customer.models import Customer

class MembershipMaster(models.Model):
    class Meta:
        db_table = 'membership_master'

    LEVEL_CHOICES = [
        ('Normal', 'Normal'),
        ('Silver', 'Silver'),
        ('Gold', 'Gold'),
        ('Platinum', 'Platinum'),
        ('Diamond', 'Diamond'),
        ('Master Gold', 'Master Gold'),
    ]

    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, unique=True)
    min_amount = models.PositiveIntegerField()
    max_amount = models.PositiveIntegerField(null=True, blank=True)  # Normal only
    service_fee = models.PositiveIntegerField()  # per 10gm
    service_fee_percent = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    daily_slot = models.PositiveIntegerField()

class CustomerWallet(models.Model):
    class Meta:
        db_table = 'customer_wallet'
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_membership = models.ForeignKey(MembershipMaster, on_delete=models.SET_NULL, null=True)

class WalletRechargeOrder(models.Model):
    class Meta:
        db_table = 'wallet_recharge_order'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

    amount = models.PositiveIntegerField()
    membership = models.ForeignKey(MembershipMaster, on_delete=models.PROTECT)

    # Razorpay Order
    razorpay_order_id = models.CharField(max_length=100, unique=True)
    currency = models.CharField(max_length=10, default="INR")

    status = models.CharField(
        max_length=20,
        choices=[
            ("Created", "Created"),
            ("Paid", "Paid"),
            ("Failed", "Failed")
        ],
        default="Created"
    )

    created_at = models.DateTimeField(auto_now_add=True)

class WalletRechargeHistory(models.Model):
    class Meta:
        db_table = 'wallet_recharge_history'

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order = models.OneToOneField(
        WalletRechargeOrder,
        on_delete=models.CASCADE
    )

    amount = models.PositiveIntegerField()
    membership_allocated = models.ForeignKey(
        MembershipMaster,
        on_delete=models.SET_NULL,
        null=True
    )

    # Razorpay Payment
    razorpay_payment_id = models.CharField(max_length=100)
    razorpay_signature = models.CharField(max_length=255)

    status = models.CharField(
        max_length=20,
        choices=[
            ("Success", "Success"),
            ("Failed", "Failed")
        ]
    )

    created_at = models.DateTimeField(auto_now_add=True)

class CustomerDemoWallet(models.Model):
    class Meta:
        db_table = 'customer_demo_wallet'
    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_membership = models.ForeignKey(MembershipMaster, on_delete=models.SET_NULL, null=True)

class WithdrawalRequest(models.Model):
    class Meta:
        db_table = 'customer_withdrawal_request'

    unique_id = models.CharField(max_length=32, unique=True)

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)

    request_amount = models.DecimalField(max_digits=12, decimal_places=2)
    email = models.CharField(max_length=255, null=True, blank=True)

    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    final_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    status = models.CharField(max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected')
        ],
        default='PENDING'
    )

    transaction_number = models.CharField(max_length=100, null=True, blank=True)

    remark = models.TextField(null=True, blank=True)

    request_date = models.DateTimeField(auto_now_add=True)
    action_date = models.DateTimeField(null=True, blank=True)

    action_by = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.customer} - {self.request_amount} ({self.status})"


class ManualRechargeRequest(models.Model):
    class Meta:
        db_table = 'manual_recharge_request'
        ordering = ['-request_date']

    unique_id = models.CharField(max_length=32, unique=True)
    customer  = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount    = models.PositiveIntegerField()
    membership = models.ForeignKey(MembershipMaster, on_delete=models.PROTECT, null=True)

    utr_number   = models.CharField(max_length=100)
    payment_mode = models.CharField(
        max_length=10,
        choices=[('UPI','UPI'),('NEFT','NEFT'),('IMPS','IMPS'),('RTGS','RTGS')],
        default='UPI'
    )
    screenshot = models.CharField(max_length=300, null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=[('PENDING','Pending'),('APPROVED','Approved'),('REJECTED','Rejected')],
        default='PENDING'
    )

    remark      = models.TextField(null=True, blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    action_date  = models.DateTimeField(null=True, blank=True)
    action_by    = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.customer} - {self.amount} ({self.status})"


class WalletManualCredit(models.Model):
    class Meta:
        db_table = 'wallet_manual_credit'
        ordering = ['-credited_on']

    unique_id    = models.CharField(max_length=32, unique=True)
    customer     = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount       = models.PositiveIntegerField()
    remark       = models.TextField()
    utr_number   = models.CharField(max_length=100, blank=True)
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after  = models.DecimalField(max_digits=12, decimal_places=2)
    credited_by  = models.CharField(max_length=50)
    credited_on  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} + ₹{self.amount} by {self.credited_by}"


class WalletManualDebit(models.Model):
    class Meta:
        db_table = 'wallet_manual_debit'
        ordering = ['-debited_on']

    unique_id      = models.CharField(max_length=32, unique=True)
    customer       = models.ForeignKey(Customer, on_delete=models.CASCADE)
    amount         = models.PositiveIntegerField()
    remark         = models.TextField()
    balance_before = models.DecimalField(max_digits=12, decimal_places=2)
    balance_after  = models.DecimalField(max_digits=12, decimal_places=2)
    debited_by     = models.CharField(max_length=50)
    debited_on     = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer} - ₹{self.amount} by {self.debited_by}"