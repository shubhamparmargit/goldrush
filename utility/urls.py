from utility.views import *
from django.urls import include, re_path, path

page_obj = Pages()
data_obj = DataList()

urlpatterns = [
    re_path(r'^javascript-disabled$', page_obj.javascript_disabled, name='javascript_disabled'),
    re_path(r'^unauthorized$', page_obj.check_role_access, name='unauthorized'),
    
    re_path(r'^data-list$', data_obj.getAllDataByTable, name='getAllDataByTable'),
    re_path(r'^exportData$', data_obj.exportData, name='exportData'),
    re_path(r'^change-access$', data_obj.changeAccess, name='changeAccess'),
    re_path(r'^change-trading-option$', data_obj.changeTradingOption, name='changeTradingOption'),
    re_path(r'^change-trading-account$', data_obj.changeTradingAccount, name='changeTradingAccount'),
]