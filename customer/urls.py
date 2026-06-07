from customer.views import *
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^customer-registration$', customerRegistarion, name='customerRegistarion'),
    re_path(r'^customer-login$', customerLogin, name='customerLogin'),
    re_path(r'^customer-profile$', profile, name='profile'),
    re_path(r'^forgot-password$', forgotPassword, name='forgotPassword'),
    
    re_path(r'^check-customer-app-access$', checkCustomerAppAccess, name='checkCustomerAppAccess'),
    re_path(r'^check-unique-app-id$', checkUniqueAppId, name='checkUniqueAppId'),
    re_path(r'^store-fcm-id$', storeFCMId, name='storeFCMId'),
    re_path(r'^store-unique-app-id$', storeUniqueAppId, name='storeUniqueAppId'),

    re_path(r'^add-customer-address$', addCustomerAddress, name='addCustomerAddress'),
    re_path(r'^update-customer-address$', updateCustomerAddress, name='updateCustomerAddress'),
    re_path(r'^customer-address-list$', customerAddressList, name='customerAddressList'),
]