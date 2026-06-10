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
    re_path(r'^save-stop-loss$', wallet_obj.save_stop_loss, name='save_stop_loss'),

    re_path(r'^withdraw-request$', widr_obj.requestWithdrawal, name='withdraw_request'),
    re_path(r'^withdraw-history$', widr_obj.getWithdrawalList, name='withdraw_history'),
    re_path(r'^update-withdrawal-status$', widr_obj.updateWithdrawalStatus, name='update_withdrawal_status'),

    path("razorpay/webhook/", razorpay_webhook, name="razorpay_webhook"),
]
