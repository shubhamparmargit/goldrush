from customer_wallet.views import *
from django.urls import include, re_path, path
from customer_wallet.views_webhook import razorpay_webhook

page_obj    = Pages()
wallet_obj  = WalletOperations()
widr_obj    = WithdrawalOperations()
manual_obj  = ManualRechargePortal()
bank_obj    = CompanyBankPortal()
awb_obj     = AddWalletBalance()

urlpatterns = [
    re_path(r'^my-wallet$', page_obj.my_wallet, name='my_wallet'),
    re_path(r'^recharge-wallet$', page_obj.recharge_wallet, name='recharge_wallet'),
    re_path(r'^withdraw-amount$', page_obj.withdraw_amount, name='withdraw_amount'),

    re_path(r'^create-wallet-order$', wallet_obj.create_wallet_order, name='create_wallet_order'),
    re_path(r'^payment-success$', wallet_obj.wallet_payment_success, name='wallet_payment_success'),
    re_path(r'^payment-failed$', wallet_obj.wallet_payment_failed, name='wallet_payment_failed'),
    re_path(r'^wallet-history-detail$', wallet_obj.wallet_history_detail, name='wallet_history_detail'),
    re_path(r'^submit-manual-recharge$', wallet_obj.submitManualRecharge, name='submit_manual_recharge'),

    re_path(r'^withdraw-request$', widr_obj.requestWithdrawal, name='withdraw_request'),
    re_path(r'^withdraw-history$', widr_obj.getWithdrawalList, name='withdraw_history'),
    re_path(r'^update-withdrawal-status$', widr_obj.updateWithdrawalStatus, name='update_withdrawal_status'),

    # Portal
    re_path(r'^portal/manual-recharge-requests$', manual_obj.manual_recharge_list_page, name='manual_recharge_list_page'),
    re_path(r'^portal/get-manual-recharge-list$', manual_obj.get_manual_recharge_list, name='get_manual_recharge_list'),
    re_path(r'^portal/approve-manual-recharge$', manual_obj.approve_manual_recharge, name='approve_manual_recharge'),
    re_path(r'^portal/reject-manual-recharge$', manual_obj.reject_manual_recharge, name='reject_manual_recharge'),

    re_path(r'^portal/company-bank-details$', bank_obj.company_bank_page, name='company_bank_page'),
    re_path(r'^portal/save-company-bank$', bank_obj.save_company_bank, name='save_company_bank'),

    re_path(r'^portal/add-wallet-balance$', awb_obj.add_wallet_page, name='add_wallet_page'),
    re_path(r'^portal/search-customer-wallet$', awb_obj.search_customer, name='search_customer_wallet'),
    re_path(r'^portal/credit-wallet$', awb_obj.credit_wallet, name='credit_wallet'),
    re_path(r'^portal/wallet-credit-history$', awb_obj.credit_history, name='wallet_credit_history'),

    path("razorpay/webhook/", razorpay_webhook, name="razorpay_webhook"),
]
