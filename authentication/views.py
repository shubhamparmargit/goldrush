from django.shortcuts import render
from utility.views import Utility, Validation, Encryption, RandomIdGenerate, PasswordUtility, current_date, urlPrefix, domainURLPortal
from authentication.models import Login, LoginReport, PasswordResetRequest
from users.models import Franchise
from users.views import TradingUser
from django.http.response import JsonResponse
from rest_framework import status
from django.db import transaction
from django.utils import timezone
import uuid
from datetime import timedelta
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from messaging_hub.views import MailNotification

mail_obj = MailNotification()
valid_obj = Validation()
util_obj = Utility()
encrypt_obj = Encryption()
random_obj = RandomIdGenerate()
pass_obj = PasswordUtility()

class Pages:
    def login(self,request):
        auth=Authentication()
        return auth.logout(request)
    
    def password_reset(self,request):
        return render(request,'portal/password-reset.html')
    
    def validate_reset_link(self, request):
        unique_id = request.GET.get('id')
        model_class = PasswordResetRequest
        context = pass_obj.generic_reset_link_validation(model_class, unique_id)
        return render(request, 'portal/set-password.html', {'context': context})

    def change_password(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/change-password.html')
        else:
            return util_obj.goToLogin(request)

class Authentication:
    def logout(self,request):
        if util_obj.checkSession(request) == False:
            session_id = request.session["session_id"]
            username = request.session["logged"]
            
            login_details = LoginReport.objects.filter(session_id=session_id, username=username)
            if login_details:
                login_details.update(
                    logout_date_time = current_date,
                )
        request.session.clear()
        return render(request,'portal/login.html')

    def login(self,request):
        if request.method == 'POST':
            try:
                if request.POST.get('btn_login') is not None and request.POST.get('btn_login')=='btn_login':
                    username=request.POST['username']
                    password=request.POST['password']
                    ip = util_obj.getIPAddress(request)
                    if (username!="" and username is not None and password!="" and password is not None):
                        mobile_validate = valid_obj.validate_mobile(username)
                        if mobile_validate != 1:
                            return util_obj.printErrorResponse_200(mobile_validate)
                        
                        login_success = Login.objects.filter(mobile_number=username)[0]
                        if not login_success:
                            return util_obj.printErrorResponse_200('Username or password is incorrect')
                        else:
                            login_id=login_success.id
                            db_pass=login_success.password
                            db_salt=login_success.salt
                            password=encrypt_obj.encryption(db_salt,password)
                            # print(db_salt)
                            # print(password)
                            if password == db_pass:
                                if(login_success.access=="Granted"):
                                    # 🔐 CHECK FRANCHISE STATUS
                                    franchise = Franchise.objects.filter(
                                        unique_id=login_success.table_id
                                    ).only('status').first()

                                    if franchise:
                                        if franchise.status != 'Approved':
                                            if franchise.status == 'Rejected':
                                                msg = 'Your franchise request was rejected by admin.'
                                            else:
                                                msg = 'Your franchise approval is pending.'
                                            return util_obj.printErrorResponse_200(msg)
                                        
                                    mob=login_success.mobile_number 
                                    login_type="Web"
                                    session_id = random_obj.generateUID()
                                
                                    with transaction.atomic():
                                        insertData = LoginReport.objects.create(
                                            username = mob,
                                            login_date_time = current_date,
                                            ip_address = ip,
                                            login_type = login_type,
                                            session_id = session_id,
                                            login = Login.objects.get(id=login_id),
                                        )
                                        if insertData:
                                            request.session['login_id']=login_id
                                            request.session['role']=login_success.role.id	
                                            request.session['name']=login_success.name	
                                            request.session['logged']=username
                                            request.session['session_id']=session_id

                                            util_obj.activity_log(login_id,username,"Login","User Logged In")

                                            return JsonResponse({'success':'1','message':'User logged in successfully','redirect':'admin-dashboard'}, status=status.HTTP_200_OK)
                                        else:
                                            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('You are blocked by the administation. Kindly contact your service provider!')
                            else:
                                return util_obj.printErrorResponse_200('Username or password is incorrect')
                    else:
                        return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')                 
                else:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
            except:
               return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
        else:
            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        
    def change_login_password(self, request):
        if request.method == 'POST':
            try:
                # Fetch data from the form
                login_id = request.session.get('login_id')  # Assuming user is logged in
                password = request.POST.get('password')
                confirm_password = request.POST.get('confirm_password')

                # Check if both password fields match
                if password != confirm_password:
                    return util_obj.printErrorResponse_200("Passwords do not match")

                # Validation: Check if password is not empty
                if not password or len(password) < 6:  # Basic password length check
                    return util_obj.printErrorResponse_200("Password is too short. Minimum 6 characters.")

                # Fetch the user details using the login_id (session)
                user = Login.objects.get(id=login_id)

                if not user:
                    return util_obj.printErrorResponse_200("User not found")

                # Encrypt the new password
                encrypt_obj = Encryption()
                salt, encrypted_password = encrypt_obj.runEncryprion(password)

                # Use transaction to ensure atomicity
                with transaction.atomic():
                    # Update the password and salt in the database
                    user.password = encrypted_password
                    user.salt = salt
                    user.password_text = password 
                    user.save()  # Save the updated user data

                    util_obj.activity_log(login_id, user.name, "Password Change", "User changed their password successfully")

                # Return success message
                return JsonResponse({
                    'success': '1',
                    'message': 'Password changed successfully'
                }, status=200)

            except Login.DoesNotExist:
                return util_obj.printErrorResponse_200('User not found')
            except Exception as e:
                return util_obj.printErrorResponse_200(f"Error: {str(e)}")
            
class Profile:
    def show_profile(self, request):
        trade_obj = TradingUser()

        try:
            # Get current logged-in user from session or request
            login_id = request.session.get('login_id')
            if not login_id:
                return JsonResponse({'success': '0', 'message': 'User not logged in'}, status=400)
            
            # Fetch user from Login table
            login_data = Login.objects.get(id=login_id)
            
            # Check user role
            user_role = login_data.role.role_name  # Get user role (e.g. Super Admin, SMRA, MRA, RA)
            user_role_id = login_data.role.id
            
            user_profile = {
                'name': login_data.name,
                'mobile': login_data.mobile_number,
                'email': login_data.email,
                'role': user_role,
                'register_date_time': timezone.localtime(login_data.date).strftime('%d-%m-%Y @ %I:%M %p'),
                'access': login_data.access,
            }

            # If user is Super Admin, show only Login table data
            if user_role_id == 1 or user_role_id == 5:
                return render(request, 'portal/profile.html', {'profile_data': user_profile})
            
            # If user is SMRA/MRA/RA, fetch Franchise and other related data
            if user_role_id in [2, 3, 4]:
                # Fetch franchise data
                franchise = Franchise.objects.filter(unique_id=login_data.table_id).select_related('parent').first()

                if franchise:
                    parent_name = ''
                    parent_referral_id = ''

                    if franchise and franchise.parent:
                        parent_name = franchise.parent.franchise_name
                        parent_referral_id = franchise.parent.referral_id

                    register_date_time = timezone.localtime(franchise.date).strftime('%d-%m-%Y @ %I:%M %p')
                    franchiseDetails = trade_obj.getFranchiseDetails(franchise.unique_id,include_bank=True,include_docs=True)

                    # Get all franchise data (all fields)
                    user_profile = {
                        'is_franchise':True,'register_date_time':register_date_time, 'role': user_role, 'unique_id':franchise.unique_id, 'franchise_name':franchise.franchise_name, 'aadhaar_number':franchise.aadhaar_number, 'pan_number':franchise.pan_number, 'mobile':franchise.mobile, 'email':franchise.email, 'referral_id':franchise.referral_id, 'franchise_model':franchise.franchise_model, 'name':franchise.holder_name, 'access':franchise.access, 'address':franchise.address, 'company_support_id':franchise.company_support_id, 'agent_id':franchise.agent_id, 'gst_number':franchise.gst_number, 'commission_slab':franchise.commission_slab, 'commission_percentage':franchise.commission_percentage, 'parent_name': parent_name,'parent_referral_id': parent_referral_id, 'franchiseDetails':franchiseDetails
                    }

                else:
                    user_profile.update({'franchise_info': 'No franchise data available'})

                return render(request, 'portal/profile.html', {'profile_data': user_profile})
            
            return JsonResponse({'success': '0', 'message': 'Invalid user role'}, status=400)

        except Login.DoesNotExist:
            return JsonResponse({'success': '0', 'message': 'User not found'}, status=400)
        except Exception as e:
            return JsonResponse({'success': '0', 'message': str(e)}, status=500)

class PasswordReset:
    def password_reset_request(self, request):
        if request.method == "POST":
            email = request.POST.get('email', '').strip()
            
            if not email:
                return JsonResponse({'success': 0, 'message': 'Email field is mandatory!'})

            # 2. Format validation (Regex and Domain check)
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({'success': 0, 'message': 'Please enter a valid email address!'})

            try:
                user = Login.objects.get(email=email, access='Granted')

                PasswordResetRequest.objects.filter(email=email, password_changed="No").update(link_status="Expired")
                
                # Generate Unique ID
                unique_id = str(uuid.uuid4())
                valid_till = timezone.now() + timedelta(hours=2)
                page_name = 'set-password'
                # valid_till = timezone.now() + timedelta(minutes=60)
                
                with transaction.atomic():
                    reset_req = PasswordResetRequest.objects.create(
                        email=email,
                        ip_address=util_obj.getIPAddress(request),
                        request_date_time=timezone.now(),
                        valid_till=valid_till,
                        unique_id=unique_id,
                        login=user,
                        reset_type="Web"
                    )
                    
                    util_obj.activity_log(user.id,email,"Password Reset Request","Sent")
                    
                    mail_obj.passwordReset(user.name, email, user.mobile_number, unique_id, page_name, domainURLPortal)
                    
                    return JsonResponse({'success': 1, 'message': 'Instructions sent to your email.'})
                    
            except Login.DoesNotExist:
                # Security tip: Industry standard mein hum "Email sent" hi dikhate hain 
                # taaki email enumeration na ho sake, par aapke code ke hisab se:
                # return JsonResponse({'success': 0, 'message': 'This email id is not registered with us...'})
                return JsonResponse({'success': 0, 'message': 'Email Sent'})
            except Exception as e:
                # return JsonResponse({'success': 0, 'message': 'Something went wrong. Please try again later.'})
                return JsonResponse({'success': 0, 'message': 'Email Sent'})

        return render(request, 'portal/password-reset.html')

    def set_new_password(self,request):
        if request.method == "POST":
            unique_id = request.POST.get('unique_id')
            password = request.POST.get('password') 
            confirm_password = request.POST.get('confirm_password')

            # 1. Mandatory Fields Check
            if not password or not confirm_password or password != confirm_password:
                return JsonResponse({'success': 0, 'message': 'Passwords do not match or fields are empty!', 'btn':True})

            try:
                reset_obj = PasswordResetRequest.objects.get(unique_id=unique_id)
                
                if reset_obj.password_changed == "Yes" or timezone.now() > reset_obj.valid_till or reset_obj.link_status=='Expired':
                    return JsonResponse({'success': 0, 'message': 'The URL you tried to use is either incorrect or no longer valid.', 'btn':True})

                try:
                    user = Login.objects.get(email=reset_obj.email, id=reset_obj.login_id, access='Granted')
                    
                    with transaction.atomic():
                        # Encrypt the new password
                        encrypt_obj = Encryption()
                        salt, encrypted_password = encrypt_obj.runEncryprion(password)
                        
                        # Update User Password
                        user.password = encrypted_password
                        user.salt = salt
                        user.password_text = password
                        user.save()

                        # Update Reset Request Status
                        reset_obj.password_changed = "Yes"
                        reset_obj.changed_date_time = timezone.now()
                        reset_obj.link_status = "Used"
                        reset_obj.save()

                        util_obj.activity_log(user.id, user.name, "Password Change", "User changed their password successfully")

                    return JsonResponse({'success': 1, 'message': 'Password Updated.', 'btn':True})

                except Login.DoesNotExist:
                    return JsonResponse({'success': 0, 'message': 'User not found or access denied.', 'btn':True})

            except PasswordResetRequest.DoesNotExist:
                return JsonResponse({'success': 0, 'message': 'The URL you tried to use is either incorrect or no longer valid.', 'btn':True})

        return JsonResponse({'success': 0, 'message': 'Invalid request method.', 'btn':True})