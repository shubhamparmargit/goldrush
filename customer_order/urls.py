from customer_order.views import *
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^cart-insert$', cartInsert, name='cartInsert'),
    re_path(r'^customer-cart-data$', customerCartData, name='customerCartData'),
    re_path(r'^cart-delete$', cartDelete, name='cartDelete'),

    re_path(r'^place-order$', placeOrder, name='placeOrder'),
    re_path(r'^order-list$', orderList, name='orderList'),
    re_path(r'^order-details$', orderDetails, name='orderDetails'),

    # re_path(r'^create-order$', create_razorpay_order, name="create_order"),
    re_path(r'^verify-payment$', verify_payment, name="verify_payment"),
]