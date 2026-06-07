from django.db import models

class Franchise(models.Model):
    unique_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    date = models.DateTimeField(auto_now_add=True)

    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
    )

    franchise_model = models.CharField(
        max_length=10,
        choices=[('SMRA','SMRA'),('MRA','MRA'),('RA','RA'),('User','User')]
    )

    company_support_id = models.CharField(max_length=20)
    referral_id = models.CharField(max_length=20, unique=True)
    referral_prefix = models.CharField(max_length=10)
    referral_sequence = models.IntegerField()

    franchise_type = models.CharField(
        max_length=5,
        choices=[('Mr','Mr'),('Mrs','Mrs'),('Ms','Ms')]
    )

    franchise_name = models.CharField(max_length=100)
    holder_name = models.CharField(max_length=100)

    aadhaar_number = models.CharField(max_length=12)
    pan_number = models.CharField(max_length=10)

    mobile = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)

    gst_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField()

    agent_id = models.CharField(max_length=50)

    commission_slab = models.DecimalField(max_digits=5, decimal_places=2)
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2)

    access = models.CharField(
        max_length=20,
        default='Blocked'
    )

    created_by = models.BigIntegerField()  # login.id

    status = models.CharField(
        max_length=20,
        default='Pending'
    )
    status_date = models.DateTimeField(null=True)

    class Meta:
        db_table = 'franchise'

class FranchiseDocuments(models.Model):
    unique_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    date = models.DateTimeField(auto_now_add=True)

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE
    )

    doc_type = models.CharField(
        max_length=20,
        choices=[
            ('AADHAAR','AADHAAR'),
            ('PAN','PAN'),
            ('PAYMENT','PAYMENT'),
            ('AGREEMENT','AGREEMENT'),
            ("BANK_CHEQUE", "Cancelled Cheque"),
            ("BANK_PASSBOOK", "Passbook"),
            ("BANK_STATEMENT", "Bank Statement"),
        ]
    )

    file_path = models.CharField(max_length=255)

    class Meta:
        db_table = 'franchise_documents'

class FranchiseBankDetails(models.Model):
    unique_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    date = models.DateTimeField(auto_now_add=True)

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE
    )

    bank_name = models.CharField(max_length=100)
    account_holder_name = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code = models.CharField(max_length=15)
    branch_name = models.CharField(max_length=100)

    class Meta:
        db_table = 'franchise_bank_details'

class Payments(models.Model):
    unique_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    franchise = models.ForeignKey(
        Franchise,
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField()
    payment_mode = models.CharField(max_length=50)

    status = models.CharField(
        max_length=20,
        choices=[
            ('Pending','Pending'),
            ('Approved','Approved'),
            ('Rejected','Rejected')
        ]
    )

    class Meta:
        db_table = 'payments'

class Commissions(models.Model):
    unique_id = models.CharField(
        max_length=32,
        unique=True,
        editable=False
    )

    date = models.DateTimeField(auto_now_add=True)

    from_franchise = models.ForeignKey(
        Franchise,
        related_name='commission_from',
        on_delete=models.CASCADE
    )

    to_franchise = models.ForeignKey(
        Franchise,
        related_name='commission_to',
        on_delete=models.CASCADE
    )

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    percentage = models.DecimalField(max_digits=5, decimal_places=2)
    slab = models.DecimalField(max_digits=5, decimal_places=2)

    class Meta:
        db_table = 'commissions'