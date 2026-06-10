from customer_reports.views import *
from django.urls import include, re_path, path

page_obj = Pages()
cust_obj = CustomerOperation()
cust_odr_obj = OrderOperation()
cust_cart_obj = CartOperation()
pdf_obj = PDFInvoice()
cleanup_obj = InactiveCustomerCleanup()

urlpatterns = [
   re_path(r'^customer-list$', page_obj.customer_list, name='customer_list'),
   re_path(r'^customer-cart-list$', page_obj.customer_cart_list, name='customer_cart_list'),
   re_path(r'^customer-order-list$', page_obj.customer_order_list, name='customer_order_list'),
   re_path(r'^registration-report$', page_obj.registration_report, name='registration_report'),
   re_path(r'^transaction-report$', page_obj.transaction_report, name='transaction_report'),
   re_path(r'^wallet-recharge-report$', page_obj.wallet_recharge_report, name='wallet_recharge_report'),
   re_path(r'^first-recharge-report$', page_obj.first_recharge_report, name='first_recharge_report'),
   re_path(r'^customer-report$', page_obj.customer_report, name='customer_report'),
   re_path(r'^customer-transfer-report$', page_obj.customer_transfer_report, name='customer_transfer_report'),
   re_path(r'^order-report$', page_obj.order_report, name='order_report'),
   re_path(r'^no-recharge-report$', page_obj.no_recharge_report, name='no_recharge_report'),
   re_path(r'^inactive-customer-report$', page_obj.inactive_customer_report, name='inactive_customer_report'),
   re_path(r'^withdrawal-report$', page_obj.withdrawal_report, name='withdrawal_report'),
   re_path(r'^ledger-report$', page_obj.ledger_report, name='ledger_report'),
   re_path(r'^get-customer-ledger$', page_obj.get_customer_ledger, name='get_customer_ledger'),
   
   re_path(r'^mac-reset$', cust_obj.macReset, name='macReset'),
   re_path(r'^getCustomer$', cust_obj.getCustomer, name='getCustomer'),
   re_path(r'^getCustomerForEdit$', cust_obj.getCustomerForEdit, name='getCustomerForEdit'),
   re_path(r'^updateCustomer$', cust_obj.updateCustomer, name='updateCustomer'),

   re_path(r'^getCustomerOrderDetails$', cust_odr_obj.getCustomerOrderDetails, name='getCustomerOrderDetails'),
   re_path(r'^updateOrderStatus$', cust_odr_obj.updateOrderStatus, name='updateOrderStatus'),

   re_path(r'^getCustomerCartDetails$', cust_cart_obj.getCustomerCartDetails, name='getCustomerCartDetails'),

   path('download_invoice/<slug:order_id>/<slug:invoice_type>', pdf_obj.download_invoice, name='download_invoice'),

   re_path(r'^inactive-cleanup$', cleanup_obj.cleanup_page, name='inactive_cleanup_page'),
   re_path(r'^inactive-cleanup/preview$', cleanup_obj.preview, name='inactive_cleanup_preview'),
   re_path(r'^inactive-cleanup/run$', cleanup_obj.run_cleanup, name='inactive_cleanup_run'),
]