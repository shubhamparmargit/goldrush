"""ornament URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.authtoken import views

urlpatterns = [
	# path('admin/', admin.site.urls),
    # re_path(r'^', include('authentication.urls')),
	# re_path(r'^', include('utility.urls')),
	# re_path(r'^', include('adminportal.urls')),
	# re_path(r'^', include('csvdata.urls')),

    # path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),

    path('admin/', admin.site.urls),
	path('api-token-auth/', views.obtain_auth_token, name='api-token-auth'),

	re_path(r'app/', include('customer.urls')),
	re_path(r'app/', include('customer_product.urls')),
	re_path(r'app/', include('customer_order.urls')),
	re_path(r'app/', include('app_misc.urls')),

	re_path(r'digital-investment/', include('customer_trading.urls')),
	re_path(r'digital-investment/', include('customer_wallet.urls')),
	re_path(r'digital-investment/', include('customer_transaction.urls')),

    re_path(r'portal/', include('authentication.urls')),
	re_path(r'portal/', include('utility.urls')),
	re_path(r'portal/', include('dashboard.urls')),
	re_path(r'portal/', include('product.urls')),
	re_path(r'portal/', include('portal_misc.urls')),
	re_path(r'portal/', include('customer_reports.urls')),
	re_path(r'portal/', include('users.urls')),
	re_path(r'portal/', include('portal_users.urls')),

	re_path(r'', include('messaging_hub.urls')),
	re_path(r'', include('website.urls')),
	re_path(r'', include('customer_authentication.urls')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

