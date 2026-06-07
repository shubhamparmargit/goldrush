from portal_users.views import *
from django.urls import include, re_path, path

page_obj = Pages()
user_obj = PortalUser()

urlpatterns = [
    re_path(r'^portal-users$', page_obj.portal_users, name='portal_users'),

    re_path(r'^addPortalUser$', user_obj.addPortalUser, name='add_portal_user'),
    re_path(r'^updatePortalUser$', user_obj.updatePortalUser, name='update_portal_user'),
    re_path(r'^getPortalUser$', user_obj.getPortalUser, name='get_portal_user'),
]