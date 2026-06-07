from customer_authentication.views import *
from django.urls import include, re_path, path

page_obj = Pages()
pass_obj = PasswordReset()

urlpatterns = [
    re_path(r'^set-customer-password$', page_obj.validate_cust_reset_link, name='validate_cust_reset_link'),

    re_path(r'^set-new-customer-password$', pass_obj.set_new_customer_password, name='set_new_customer_password')
]