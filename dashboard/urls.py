from dashboard.views import *
from django.urls import include, re_path, path

page_obj = Pages()

urlpatterns = [
    re_path(r'^admin-dashboard$', page_obj.dashboard, name='dashboard'),
]