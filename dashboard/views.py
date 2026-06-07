from django.shortcuts import render
from utility.views import Utility

util_obj = Utility()

class Pages:
    def dashboard(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/admin-dashboard.html')
        else:
            return util_obj.goToLogin(request)