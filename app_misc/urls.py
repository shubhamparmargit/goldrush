from app_misc.views import *
from django.urls import include, re_path, path

urlpatterns = [
    re_path(r'^app-version$', checkAppVersion, name='checkAppVersion'),
    re_path(r'^image-slider$', imageSlider, name='imageSlider'),
    re_path(r'^options$', options, name='options'),
    re_path(r'^getPincodeDetails/(?P<pincode>\d{6})$',getPincodeDetails,name='getPincodeDetails'),
]