from website.views import *
from django.urls import include, re_path, path

page_obj = Pages()
enq_obj = Enquiry()

urlpatterns = [
    re_path(r'^$', page_obj.index, name='index'),
    re_path(r'^index$', page_obj.index, name='index'),
    re_path(r'^contact$', page_obj.contact, name='contact'),
    re_path(r'^ecomm-privacy-policy$', page_obj.ecomm_privacy_policy, name='ecomm_privacy_policy'),
    re_path(r'^digital-privacy-policy$', page_obj.digital_privacy_policy, name='digital_privacy_policy'),
    re_path(r'^refund-policy$', page_obj.refund_policy, name='refund_policy'),
    re_path(r'^shipping-policy$', page_obj.shipping_policy, name='shipping_policy'),
    re_path(r'^app-terms-condition$', page_obj.app_terms_condition, name='app_terms_condition'),
    re_path(r'^ecomm-terms-condition$', page_obj.ecomm_terms_condition, name='ecomm_terms_condition'),
    re_path(r'^digital-terms-condition$', page_obj.digital_terms_condition, name='digital_terms_condition'),
    re_path(r'^customer-ecomm-agreement$', page_obj.customer_ecomm_agreement, name='customer_ecomm_agreement'),
    re_path(r'^customer-digital-agreement$', page_obj.customer_digital_agreement, name='customer_digital_agreement'),
    re_path(r'^welcome-letter$', page_obj.welcome_letter, name='welcome_letter'),

    re_path(r'^contact-submit$', enq_obj.contact_submit, name='contact_submit'),
]