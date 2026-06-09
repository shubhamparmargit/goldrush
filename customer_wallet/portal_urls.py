from django.urls import re_path
from customer_wallet.views import ManualRechargePortal, CompanyBankPortal, AddWalletBalance

manual_obj  = ManualRechargePortal()
bank_obj    = CompanyBankPortal()
awb_obj     = AddWalletBalance()

urlpatterns = [
    re_path(r'^manual-recharge-requests$', manual_obj.manual_recharge_list_page, name='manual_recharge_list_page'),
    re_path(r'^get-manual-recharge-list$', manual_obj.get_manual_recharge_list, name='get_manual_recharge_list'),
    re_path(r'^approve-manual-recharge$', manual_obj.approve_manual_recharge, name='approve_manual_recharge'),
    re_path(r'^reject-manual-recharge$', manual_obj.reject_manual_recharge, name='reject_manual_recharge'),

    re_path(r'^company-bank-details$', bank_obj.company_bank_page, name='company_bank_page'),
    re_path(r'^save-company-bank$', bank_obj.save_company_bank, name='save_company_bank'),

    re_path(r'^add-wallet-balance$', awb_obj.add_wallet_page, name='add_wallet_page'),
    re_path(r'^search-customer-wallet$', awb_obj.search_customer, name='search_customer_wallet'),
    re_path(r'^credit-wallet$', awb_obj.credit_wallet, name='credit_wallet'),
    re_path(r'^debit-wallet$', awb_obj.debit_wallet, name='debit_wallet'),
    re_path(r'^wallet-credit-history$', awb_obj.credit_history, name='wallet_credit_history'),
]
