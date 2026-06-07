from django.db import models

class Customer(models.Model):
    class Meta:
        db_table = 'customer'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    name = models.CharField(max_length=50, blank=False, null=False, default='')
    aadhaar_number = models.CharField(max_length=12, unique=True)
    aadhaar_front_image = models.CharField(max_length=300, blank=False, null=False, default='')
    aadhaar_back_image = models.CharField(max_length=300, blank=False, null=False, default='')
    pan_number = models.CharField(max_length=10, unique=True)
    pan_front_image = models.CharField(max_length=300, blank=False, null=False, default='')
    mobile = models.CharField(max_length=10,unique=True)
    email = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=64)
    salt = models.CharField(max_length=64)
    password_text = models.CharField(max_length=200, blank=False, default='')
    referral_code = models.CharField(max_length=200, blank=False, default='')
    access = models.CharField(max_length=20, blank=False, default='Granted')
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)
    unique_application_id = models.CharField(max_length=300, null=True, default='')
    app_id_date = models.DateTimeField(null=True)
    device_details = models.BinaryField(null=True)
    fcm_registered_id = models.CharField(max_length=300, null=True, default='')
    fcm_date = models.DateTimeField(null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.BinaryField()
    mac_reset_count = models.IntegerField(default=0, null=True)
    trading = models.CharField(max_length=5, blank=False, default='OFF')

class CustomerAddress(models.Model):
    class Meta:
        db_table = 'customer_address'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    name = models.CharField(max_length=50, blank=False, null=True, default='')
    mobile = models.CharField(max_length=10, null=True)
    pincode = models.CharField(max_length=6,blank=False, null=False)
    postoffice = models.CharField(max_length=50, blank=False, null=False, default='')
    state = models.CharField(max_length=50, blank=False, null=False, default='')
    city = models.CharField(max_length=50, blank=False, null=False, default='')
    district = models.CharField(max_length=50, blank=False, null=False, default='')
    region = models.CharField(max_length=50, blank=False, null=False, default='')
    address_line_1 = models.CharField(max_length=255, blank=False, null=False, default='')
    address_line_2 = models.CharField(max_length=255, blank=False, null=False, default='')
    access = models.CharField(max_length=20, blank=False, default='Granted')
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')

class CustomerLoginReport(models.Model):
    class Meta:
        db_table = 'customer_login_report'
    username = models.CharField(max_length=20, blank=False, default='')
    login_date_time = models.DateTimeField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    location = models.BinaryField()
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')

class PasswordResetRequest(models.Model):
    class Meta:
        db_table = 'customer_password_reset_request'
    email = models.CharField(max_length=100, blank=False, default='')
    request_date_time = models.DateTimeField()
    valid_till = models.DateTimeField()
    password_changed = models.CharField(max_length=10, blank=False, default='No')
    changed_date_time = models.DateTimeField(null=True,blank=True,default=None)
    unique_id = models.CharField(unique=True, null=False, max_length=300, blank=False, default='')
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)
    link_status = models.CharField(max_length=20, blank=False, default='Unused')

class MacResetDetails(models.Model):
    class Meta:
        db_table = 'customer_mac_reset_details'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    old_unique_application_id = models.CharField(max_length=300, null=True, default='')
    old_app_id_date = models.DateTimeField()
    device_details = models.BinaryField(null=True)
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    added_by = models.CharField(max_length=50, blank=False, default='')

class ReferralHistory(models.Model):
    class Meta:
        db_table = 'referral_history'
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    old_referral_code = models.CharField(max_length=50)
    new_referral_code = models.CharField(max_length=50)
    transfer_date = models.DateTimeField(auto_now_add=True)
    reason_for_transfer = models.TextField(null=True, blank=True)
    transfer_by = models.CharField(max_length=50)