from customer_trading.views import *
from django.urls import include, re_path, path

page_obj = Pages()
onboard_obj = TradingOnboard()
log_obj = TradingAuth()
pin_obj = TradingPinRecovery()

urlpatterns = [
    re_path(r'^bridge$', page_obj.trading_bridge_verify, name='trading_bridge_verify'),
    re_path(r'^$', page_obj.digital_gateway, name='digital_gateway'),
    re_path(r'^digital-dashboard$', page_obj.digital_dashboard, name='digital_dashboard'),
    re_path(r'^logout-page$', page_obj.trading_logout_page, name='trading_logout_page'),
    re_path(r'^forgot-pin$', page_obj.trading_forgot_pin, name='trading_forgot_pin'),
    re_path(r'^verify-otp$', page_obj.trading_verify_otp, name='trading_verify_otp'),
    re_path(r'^reset-pin$', page_obj.trading_reset_pin, name='trading_reset_pin'),

    # re_path(r'^error$', page_obj.error_page, name='error_page'),
    # re_path(r'^bank$', page_obj.bank_page, name='bank_page'),
    # re_path(r'^login$', page_obj.login_page, name='login_page'),
    # re_path(r'^pending$', page_obj.pending_page, name='pending_page'),
    # re_path(r'^terms$', page_obj.terms_page, name='terms_page'),

    re_path(r'^saveCutomerBankDetails$', onboard_obj.saveCutomerBankDetails, name='saveCutomerBankDetails'),
    re_path(r'^saveCutomerTermsDetails$', onboard_obj.saveCutomerTermsDetails, name='saveCutomerTermsDetails'),
    re_path(r'^updateTradingStatus', onboard_obj.update_trading_status, name='update_trading_status'),
    re_path(r'^getTradingDetails$', onboard_obj.getTradingDetails, name='getTradingDetails'),

    # re_path(r'^digital-auth-login$', log_obj.trading_login, name='trading_login'),
    re_path(r'^handle-pin$', log_obj.handle_pin_action, name='handle_pin_action'),
    re_path(r'^logout$', log_obj.trading_logout, name='trading_logout'),
    re_path(r'^profile$', log_obj.trading_profile, name='trading_profile'),

    re_path(r'^send-pin-otp$', pin_obj.send_pin_otp, name='send_pin_otp'),
    re_path(r'^verify-pin-otp$', pin_obj.verify_pin_otp, name='verify_pin_otp'),
    re_path(r'^reset-trading-pin$', pin_obj.reset_trading_pin, name='reset_trading_pin'),

    re_path(r'^customer-trading-access$', checkCustomerTradingAccess, name='checkCustomerTradingAccess'),
    re_path(r'^initiate$', initiate_trading_handshake, name='initiate_trading_handshake'),
]