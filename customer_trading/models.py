from django.db import models
from customer.models import Customer
from users.models import Franchise

class CustomerTradingAccount(models.Model):
    class Meta:
        db_table = 'customer_trading_account'
    unique_id = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
    ra = models.ForeignKey(Franchise,on_delete=models.SET_NULL,null=True,limit_choices_to={'franchise_model': 'RA'})
    trading_enabled = models.CharField(max_length=5,choices=[('ON','ON'), ('OFF','OFF')],default='OFF')
    status = models.CharField(max_length=20,choices=[('Pending','Pending'), ('Approved','Approved'), ('Rejected','Rejected')],default='Pending')
    approved_by = models.BigIntegerField(null=True)  # login.id (RA)
    approved_date = models.DateTimeField(null=True)
    is_blocked = models.CharField(max_length=5, default='No')
    account_type = models.CharField(max_length=10,choices=(('LIVE','Live'), ('DEMO','Demo')),default='DEMO')

class CustomerTradingBankDetails(models.Model):
    class Meta:
        db_table = 'customer_trading_bank_details'
    unique_id = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=15)
    branch_name = models.CharField(max_length=100)
    verified = models.CharField(max_length=5, default='No')

class CustomerTradingDocuments(models.Model):
    class Meta:
        db_table = 'customer_trading_documents'
    unique_id = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    doc_type = models.CharField(
        max_length=20,
        choices=[
            ('AADHAAR','AADHAAR'),
            ('PAN','PAN'),
            ("BANK_CHEQUE", "Cancelled Cheque"),
            ("BANK_PASSBOOK", "Passbook"),
            ("BANK_STATEMENT", "Bank Statement"),
        ]
    )
    file_path = models.CharField(max_length=255)
    
class CustomerTradingTerms(models.Model):
    class Meta:
        db_table = 'customer_trading_terms'
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
    version = models.CharField(max_length=20)
    accepted = models.CharField(max_length=5, default='No')
    accepted_date = models.DateTimeField(null=True)
    accepted_ip = models.CharField(max_length=50)

# class CustomerTradingLogin(models.Model):
#     class Meta:
#         db_table = 'customer_trading_login'
#     customer = models.OneToOneField(Customer,on_delete=models.CASCADE)
#     password_text = models.CharField(max_length=200, blank=False, default='')
#     trading_password = models.CharField(max_length=64)
#     salt = models.CharField(max_length=64)
#     last_login = models.DateTimeField(null=True)
#     last_login_ip = models.CharField(max_length=50)

# class CustomerTradingLoginReport(models.Model):
#     class Meta:
#         db_table = 'customer_trading_login_report'

#     date = models.DateTimeField(auto_now_add=True)
#     trading_account = models.ForeignKey(CustomerTradingAccount, on_delete=models.CASCADE)
#     login_ip = models.CharField(max_length=45)  # IPv4 + IPv6
#     user_agent = models.TextField()  # browser + OS + device info
#     session_id = models.CharField(max_length=100, null=True, blank=True)
#     login_type = models.CharField(max_length=20, default='Web')  # Web / Mobile / App


class CustomerTradingLogin(models.Model):
    class Meta:
        db_table = 'customer_trading_login'

    customer = models.OneToOneField(Customer, on_delete=models.CASCADE)

    # 🔐 PIN Security
    pin_hash = models.CharField(max_length=64)
    pin_salt = models.CharField(max_length=64)
    pin_set = models.BooleanField(default=False)
    pin = models.IntegerField(default=0)

    # 🚫 Security Lock Mechanism
    wrong_attempts = models.IntegerField(default=0)
    lock_until = models.DateTimeField(null=True, blank=True)

    # 📊 Audit Info
    last_login = models.DateTimeField(null=True, blank=True)
    last_login_ip = models.CharField(max_length=50, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerTradingLoginReport(models.Model):
    class Meta:
        db_table = 'customer_trading_login_report'
        ordering = ['-date']

    date = models.DateTimeField(auto_now_add=True)
    trading_account = models.ForeignKey(CustomerTradingAccount, on_delete=models.CASCADE)

    login_ip = models.CharField(max_length=45)
    user_agent = models.TextField()

    login_type = models.CharField(
        max_length=20,
        choices=[
            ('WEB', 'Web'),
            ('APP', 'App'),
        ],
        default='WEB'
    )

    status = models.CharField(
        max_length=10,
        choices=[
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('LOCKED', 'Locked'),
        ],
        default='SUCCESS'
    )