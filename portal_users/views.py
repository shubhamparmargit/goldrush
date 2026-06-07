from django.shortcuts import render
from utility.views import Utility, RandomIdGenerate, Encryption, Validation, current_date, ROLE_FRANCHISE_MAP, urlPrefix
from django.http.response import JsonResponse
from rest_framework import status
import os
from django.db import transaction
from authentication.models import Login, User_Role
from django.db.models import Max
from django.conf import settings
from messaging_hub.views import MailNotification
from django.utils import timezone

util_obj = Utility()
random_obj = RandomIdGenerate()
encrypt_obj = Encryption()
valid_obj = Validation()
mail_obj = MailNotification()

class Pages:
    def portal_users(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/portal-users.html')
        else:
            return util_obj.goToLogin(request)

class PortalUser:
    def addPortalUser(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    # ================= FETCH FORM DATA =================
                    name = request.POST.get("name")
                    mobile = request.POST.get("mobile_number")
                    email = request.POST.get("email")

                    access = "Granted" if request.POST.get("access") else "Blocked"

                    # ================= CHECK MOBILE EMAIL =================
                    if not util_obj.is_mobile_email_available(mobile, email):
                        return JsonResponse({"success": '0', "message": "Mobile number or Email already registered."}, status=status.HTTP_200_OK)
                    
                    # ================= FETCH SESSION =================
                    login_id = request.session['login_id']
                    username = request.session['logged']

                    # ================= GENERATE UNIQUE IDS =================
                    unique_id = random_obj.generateUID()

                    # ================= GENERATE PASSWORD DATA =================
                    password_text = random_obj.generate_short_uuid(10)
                    salt, password = encrypt_obj.runEncryprion(password_text)

                    # ================= GET ROLE =================
                    role = User_Role.objects.get(role_name="Admin")

                    with transaction.atomic():
                        # ================= CREATE LOGIN =================
                        login = Login.objects.create(
                            date=current_date,
                            name=name,
                            mobile_number=mobile,
                            email=email,
                            password=password,
                            salt=salt,
                            password_text=password_text,
                            access=access,
                            role=role,
                            added_by=username,
                            table_name = 'login',
                            table_id = unique_id
                        )

                        util_obj.activity_log(login_id, username, "Admin", f"Admin Created => {unique_id}")

                        return JsonResponse({
                            "success": 1,
                            "message": "User created successfully"
                        })
                except Exception as e:
                    return JsonResponse({
                        "success": 0,
                        "message": "Something went wrong",
                        "error": str(e)
                    }, status=status.HTTP_200_OK)
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getPortalUser(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('portal_user') is not None:
                        unique_id = request.POST.get("unique_id", "").strip()

                        if not unique_id:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                            
                        digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                        if digit_validate != 1:
                            return util_obj.printErrorResponse_200(digit_validate)

                        user = Login.objects.filter(table_id=unique_id).first()

                        if not user:
                            return util_obj.printErrorResponse_200('Data not found!')
                              
                        data = {'success':'1','unique_id':user.table_id, 'name':user.name, 'mobile_number':user.mobile_number, 'email':user.email, 'access':user.access, 'password':user.password_text}
                                
                        return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
                    
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                
                except Exception as e:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            
            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        
        return util_obj.goToLogin(request)
    
    def updatePortalUser(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    # ================= FETCH FORM DATA =================
                    unique_id = request.POST.get("user_id")
                    name = request.POST.get("name")
                    mobile = request.POST.get("mobile_number")
                    email = request.POST.get("email")
                    password_text = request.POST.get("password")

                    # ================= CHECK MOBILE EMAIL =================
                    if not util_obj.is_mobile_email_available(mobile, email, unique_id):
                        return JsonResponse({"success": '0',"message": "Mobile number or Email already registered."}, status=status.HTTP_200_OK)
                    
                    # ================= FETCH SESSION =================
                    login_id = request.session['login_id']
                    username = request.session['logged']
                    
                    # ================= GENERATE PASSWORD DATA =================
                    salt, password = encrypt_obj.runEncryprion(password_text)

                    with transaction.atomic():
                        # ================= CREATE LOGIN =================
                        login = Login.objects.filter(table_id=unique_id).first()

                        if login:
                            login.name = name
                            login.mobile_number = mobile
                            login.email = email
                            login.password = password
                            login.salt = salt
                            login.password_text = password_text
                            login.save()

                        util_obj.activity_log(login_id, username, "Admin", f"Admin Updated => {unique_id}")

                        return JsonResponse({
                            "success": 1,
                            "message": "User Updated successfully"
                        })
                except Exception as e:
                    return JsonResponse({
                        "success": 0,
                        "message": "Something went wrong",
                        "error": str(e)
                    }, status=status.HTTP_200_OK)
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
