from django.db import models

class User_Role(models.Model):
    class Meta:
        db_table = 'user_role'
    role_name = models.CharField(max_length=100, blank=False, default='')

    @classmethod
    def get_by_franchise_model(cls, franchise_model):
        role_map = {
            "SMRA": "Supper Master Referral Agent",
            "MRA": "Master Referral Agent",
            "RA": "Referral Agent",
        }
        return cls.objects.get(role_name=role_map[franchise_model])

class Login(models.Model):
    class Meta:
        db_table = 'login'
    date = models.DateTimeField()
    name = models.CharField(max_length=200, blank=False, default='')
    mobile_number = models.CharField(max_length=10, blank=False, null=False, unique=True, default='')
    email = models.CharField(max_length=100, blank=False, null=False, unique=True, default='')
    password = models.CharField(max_length=64)
    salt = models.CharField(max_length=64)
    password_text = models.CharField(max_length=200, blank=False, default='')
    access = models.CharField(max_length=20, blank=False, default='')
    role = models.ForeignKey(User_Role,on_delete=models.SET_DEFAULT,default='')
    added_by = models.CharField(max_length=20, blank=False, default='')
    table_name = models.CharField(max_length=50, blank=False, default='')
    table_id = models.CharField(max_length=32, blank=False, default='')
    profile_img = models.CharField(max_length=300, blank=False, default='img/no-image.png')
    uniqueApplicationID = models.CharField(max_length=500, blank=False, unique=True, null=True)
    app_id_date = models.DateTimeField(null=True)
    device_details = models.CharField(max_length=300, blank=False, default='')
    fcm_registered_id = models.CharField(max_length=500, blank=False, unique=True, null=True)
    fcm_date = models.DateTimeField(null=True)
    mac_reset_count = models.IntegerField(default=0)

class LoginReport(models.Model):
    class Meta:
        db_table = 'login_report'
    username = models.CharField(max_length=20, blank=False, default='')
    login_date_time = models.DateTimeField()
    logout_date_time = models.DateTimeField(null=True)
    login_type = models.CharField(max_length=10, blank=False, default='')
    ip_address = models.GenericIPAddressField()
    session_id = models.CharField(max_length=100, blank=True, unique=True, null=True, db_index=True)
    login = models.ForeignKey(Login,on_delete=models.SET_DEFAULT,default='')

class Mac_Reset_Details(models.Model):
   class Meta:
        db_table = 'mac_reset_details'
   date = models.DateTimeField()
   unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
   old_uniqueApplicationID = models.CharField(max_length=500, blank=False, default='')
   old_app_id_date = models.DateTimeField(null=True)
   old_device_details = models.CharField(max_length=300, blank=False, default='')
   added_by = models.CharField(max_length=20, blank=False, default='')

class PasswordResetRequest(models.Model):
    class Meta:
        db_table = 'password_reset_request'
    email = models.CharField(max_length=100, blank=False, default='')
    ip_address = models.GenericIPAddressField()
    request_date_time = models.DateTimeField()
    valid_till = models.DateTimeField()
    password_changed = models.CharField(max_length=10, blank=False, default='No')
    changed_date_time = models.DateTimeField(null=True,blank=True,default=None)
    unique_id = models.CharField(unique=True, null=False, max_length=300, blank=False, default='')
    login = models.ForeignKey(Login,on_delete=models.SET_DEFAULT,default='')
    reset_type = models.CharField(max_length=20, blank=False, default='')
    link_status = models.CharField(max_length=20, blank=False, default='Unused')

class User_Activity_Log(models.Model):
    class Meta:
        db_table = 'user_activity_log'
    date = models.DateTimeField()
    username = models.CharField(max_length=20, blank=False, default='')
    page_name = models.CharField(max_length=200, blank=False, default='')
    message = models.BinaryField()
    login = models.ForeignKey(Login,on_delete=models.SET_DEFAULT,default='')