from customer_transaction.views import *
from django.urls import include, re_path, path

page_obj = Pages()
trans_obj = TransactionBuySell()
od_obj = OrderList()

urlpatterns = [
    # re_path(r'^weights$', page_obj.weights, name='weights'),
    re_path(r'^weights/(?P<metal_type>gold|silver)$', page_obj.weights, name='weights'),
    re_path(r'^live-orders$', page_obj.live_orders, name='live_orders'),
    re_path(r'^past-orders$', page_obj.past_orders, name='past_orders'),

    re_path(r'^order-calculation$', trans_obj.order_calculation, name='order_calculation'),
    re_path(r'^buy-metal$', trans_obj.buy_metal, name='buy_metal'),
    re_path(r'^sell-metal$', trans_obj.sell_metal, name='sell_metal'),
    re_path(r'^update-auto-sell$', trans_obj.update_auto_sell, name='update_auto_sell'),

    re_path(r'^live-orders-pnl$', od_obj.live_orders_pnl, name='live_orders_pnl'),
    re_path(r'^live-order-details$', od_obj.live_order_details, name='live_order_details'),
    re_path(r'^past-order-details$', od_obj.past_order_details, name='past_order_details'),

    re_path(r'^getMetalLiveRate$', getMetalData, name='getMetalData'),
]