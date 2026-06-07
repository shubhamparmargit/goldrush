from customer_product.views import *
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^categories$', categories, name='categories'),
    re_path(r'^products$', products, name='products'),
    re_path(r'^product-detail$', product_detail, name='product_detail'),
]