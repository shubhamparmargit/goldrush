from dashboard.views import *
from django.urls import include, re_path, path

page_obj = Pages()

urlpatterns = [
    re_path(r'^admin-dashboard$', page_obj.dashboard, name='dashboard'),
    re_path(r'^get-dashboard-metrics$', page_obj.get_dashboard_metrics, name='get_dashboard_metrics'),
]