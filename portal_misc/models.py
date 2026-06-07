from django.db import models

class BankHoliday(models.Model):
    class Meta:
        db_table = 'bank_holidays'
        ordering = ['date']

    date = models.DateField(unique=True)
    description = models.CharField(max_length=200)
    is_active = models.BooleanField(default=True)
    added_by = models.CharField(max_length=50)
    added_on = models.DateTimeField(auto_now_add=True)

class CompanyBankDetails(models.Model):
    class Meta:
        db_table = 'company_bank_details'

    account_name   = models.CharField(max_length=100)
    bank_name      = models.CharField(max_length=100)
    account_number = models.CharField(max_length=30)
    ifsc_code      = models.CharField(max_length=15)
    branch_name    = models.CharField(max_length=100, blank=True)
    upi_id         = models.CharField(max_length=100, blank=True)
    qr_code_image  = models.CharField(max_length=300, blank=True)
    is_active      = models.BooleanField(default=True)
    updated_on     = models.DateTimeField(auto_now=True)

class ImageSlider(models.Model):
    class Meta:
        db_table = 'image_slider'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    image_type = models.CharField(max_length=30, blank=False, null=False, default='')
    sequence = models.IntegerField()
    image = models.CharField(max_length=500, blank=False, null=False, default='')
    access = models.CharField(max_length=20, blank=False, null=False, default='')
    added_by = models.CharField(max_length=20, blank=False, null=False, default='')