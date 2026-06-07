from users.views import *
from django.urls import include, re_path, path

page_obj = Pages()
user_obj = TradingUser()

urlpatterns = [
    re_path(r'^franchise-module$', page_obj.franchise_module, name='franchise_module'),
    re_path(r'^franchise-list$', page_obj.franchise_list, name='franchise_list'),

    re_path(r'^saveTradingUser$', user_obj.saveTradingUser, name='saveTradingUser'),
    re_path(r'^getUser$', user_obj.getUser, name='getUser'),
    re_path(r'^getParentFranchises$', user_obj.getParentFranchises, name='getParentFranchises'),
    re_path(r'^franchiseHierarchy', user_obj.franchise_hierarchy, name='franchise_hierarchy'),
    re_path(r'^updateFranchiseStatus', user_obj.update_franchise_status, name='update_franchise_status'),
    re_path(r'^getAllAgents', user_obj.getAllAgents, name='getAllAgents'),
    re_path(r'^transferAgent', user_obj.transferAgent, name='transferAgent'),
]