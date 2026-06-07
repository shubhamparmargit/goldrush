from authentication.views import *
from django.urls import include, re_path, path

page_obj = Pages()
auth_obj = Authentication()
prof_obj = Profile()
pass_obj = PasswordReset()

urlpatterns = [
    re_path(r'^$', page_obj.login, name='login'),
    re_path(r'^sign-in$', page_obj.login, name='login'),
    re_path(r'^change-password$', page_obj.change_password, name='change_password'),
    re_path(r'^password-reset$', page_obj.password_reset, name='password_reset'),
    re_path(r'^set-password$', page_obj.validate_reset_link, name='validate_reset_link'),

    re_path(r'^auth-login$', auth_obj.login, name='auth_login'),
    re_path(r'^auth-logout$', auth_obj.logout, name='auth_logout'),
    re_path(r'^auth-change-password$', auth_obj.change_login_password, name='change_login_password'),

    re_path(r'^show-profile$', prof_obj.show_profile, name='show_profile'),

    re_path(r'^password-reset-request$', pass_obj.password_reset_request, name='password_reset_request'),
    re_path(r'^set-new-password$', pass_obj.set_new_password, name='set_new_password')
]