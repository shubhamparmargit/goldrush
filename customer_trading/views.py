from django.shortcuts import render, redirect
from customer.models import Customer, CustomerAddress
from customer_trading.models import CustomerTradingAccount, CustomerTradingBankDetails, CustomerTradingTerms, CustomerTradingDocuments, CustomerTradingLogin, CustomerTradingLoginReport
from utility.views import RandomIdGenerate, current_date, Utility, Validation, urlPrefix, Encryption, CustomerUtil, ProfileUtil, PinResetKeys
import re, os, secrets, jwt, datetime, time, random
from django.http.response import JsonResponse
from rest_framework import status
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from messaging_hub.views import MailNotification
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from django.core.cache import cache
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.utils import timezone
from customer_trading.decorators import require_trading_pin, require_trading_auth
from customer_transaction.views import getMetalRate

util_obj = Utility()
random_obj = RandomIdGenerate()
valid_obj = Validation()
encrypt_obj = Encryption()
mail_obj = MailNotification()
cust_util_obj = CustomerUtil()

class Pages:
    def trading_bridge_verify(self, request):
        try:
            # 1️⃣ Get token from URL (GET, not POST)
            token = request.GET.get("token", "").strip()
            device_id = request.GET.get("device_id", "").strip()

            if not token or not device_id:
                return render(request, 'digital-investment/error.html', {'msg': 'Invalid request'})

            # 2️⃣ Fetch OTT from cache
            cache_key = f"OTT:{token}"
            payload = cache.get(cache_key)

            if not payload:
                return render(request, 'digital-investment/error.html', {'msg': 'Session expired. Please try again.'})

            # 3️⃣ Device match
            if payload.get("device_id") != device_id:
                cache.delete(cache_key)
                return render(request, 'digital-investment/error.html', {'msg': 'Device mismatch.'})

            # if payload.get("ip") != util_obj.getIPAddress(request):
            #     cache.delete(cache_key)
            #     return render(request, 'digital-investment/error.html', {'msg': 'Invalid Data.'})

            # 4️⃣ Delete OTT (one-time use)
            cache.delete(cache_key)

            customer_id = payload.get("customer_id")
            if not customer_id:
                return render(request, 'digital-investment/error.html', {'msg': 'Invalid session data.'})

            customer = Customer.objects.get(id=customer_id)

            # 5️⃣ Generate JWT using SimpleJWT
            refresh = RefreshToken.for_user(customer)

            # Custom claims
            refresh["customer_uid"] = payload.get("customer_uid")
            refresh["mobile"] = customer.mobile
            refresh["trading_access"] = True
            refresh["device_id"] = device_id
            refresh["ip"] = payload.get("ip")
            refresh["app_version"] = payload.get("app_version")
            refresh["is_pin_verified"] = False

            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Optional: clear active OTT pointer
            cache.delete(f"USER_ACTIVE_OTT:{customer.id}")

            # 6️⃣ Redirect to Gateway
            response = redirect('digital_gateway')

            response.set_cookie(
                'access_token',
                access_token,
                httponly=True,
                secure=not settings.DEBUG,      # Ensure HTTPS in production
                samesite='Strict',
                max_age=900
            )

            response.set_cookie(
                'refresh_token',
                refresh_token,
                httponly=True,
                secure=not settings.DEBUG,
                samesite='Strict',
                max_age=604800
            )

            return response

        except Exception:
            return render(request, 'digital-investment/error.html', {
                'msg': 'Internal server error during handshake.'
            })
    
    def digital_gateway(self, request):
        if request.trading_error:
            return render(request, 'digital-investment/error.html', {'msg': request.trading_error})

        customer = request.trading_customer
        validated_token = request.validated_token

        # print("customer",customer)
        
        trading_account = CustomerTradingAccount.objects.filter(customer=customer,trading_enabled='ON',is_blocked='No').first()

        if not trading_account:
            return render(request, 'digital-investment/error.html', {'msg': 'Digital investment access is disabled or invalid request'})

        # 2️⃣ Terms check
        terms = CustomerTradingTerms.objects.filter(customer=customer,accepted='Yes').first()
        if not terms:
            return render(request, 'digital-investment/terms.html')

        # 3️⃣ RA approval check
        if trading_account.status != 'Approved':
            return render(request, 'digital-investment/pending.html')
        
        # 4️⃣ 🔐 PIN LOGIC STARTS HERE

        login_entry = CustomerTradingLogin.objects.filter(customer=customer).first()

        # 1️⃣ PIN Setup Required
        if not login_entry or not login_entry.pin_set:
            return render(request, 'digital-investment/pin-auth.html', {
                'mode': 'setup',
                'customer_name': customer.name
            })

        # # 2️⃣ PIN Verify Required
        # if not validated_token.get('is_pin_verified'):

        #     # Lock Check
        #     if login_entry.lock_until and login_entry.lock_until > timezone.now():
        #         return render(request, 'digital-investment/pin-auth.html', {
        #             'mode': 'verify',
        #             'locked_until': login_entry.lock_until,
        #             'customer_name': customer.name
        #         })

        #     attempts_remaining = None
        #     if login_entry.wrong_attempts > 0:
        #         attempts_remaining = 5 - login_entry.wrong_attempts

        #     return render(request, 'digital-investment/pin-auth.html', {
        #         'mode': 'verify',
        #         'customer_name': customer.name,
        #         'attempts_remaining': attempts_remaining
        #     })

        # 2️⃣ PIN Verify Required (Sliding TTL Version)

        pin_key = cust_util_obj.get_pin_cache_key(customer.id)

        # If PIN session expired
        if not cache.get(pin_key):

            # Lock Check
            if login_entry.lock_until and login_entry.lock_until > timezone.now():
                return render(request, 'digital-investment/pin-auth.html', {
                    'mode': 'verify',
                    'locked_until': login_entry.lock_until,
                    'customer_name': customer.name
                })

            attempts_remaining = None
            if login_entry.wrong_attempts > 0:
                attempts_remaining = 5 - login_entry.wrong_attempts

            return render(request, 'digital-investment/pin-auth.html', {
                'mode': 'verify',
                'customer_name': customer.name,
                'attempts_remaining': attempts_remaining
            })

        # 🔄 Sliding TTL Refresh (User Active)
        cache.set(pin_key, True, timeout=settings.PIN_TTL_SECONDS)

        # 5️⃣ Final Dashboard
        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)
        return render(request, 'digital-investment/digital-dashboard.html', {
            'wallet_balance': wallet_balance,
            'customer_name': customer.name
        })

    @require_trading_pin
    def digital_dashboard(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')

        # pin_key = cust_util_obj.get_pin_cache_key(customer.id)

        # if not cache.get(pin_key):
        #     return redirect('digital_gateway')

        # # 🔄 Sliding refresh
        # cache.set(pin_key, True, timeout=settings.PIN_TTL_SECONDS)

        wallet_balance = cust_util_obj.get_wallet_balance(customer, request)

        try:
            metal = getMetalRate()
            current_gold_rate = metal["buy_gold_rate"]
            current_silver_rate = metal["buy_silver_rate"]
            currency_icon = metal["currency_icon"]
        except Exception:
            return JsonResponse({
                "status": False,
                "message": "Unable to fetch gold rate"
            })

        # print("dashboard :: ", current_gold_rate)

        return render(request, 'digital-investment/digital-dashboard.html', {
            'wallet_balance': wallet_balance,
            'customer_name': customer.name,
            'current_gold_rate': current_gold_rate,
            'current_silver_rate': current_silver_rate,
            'currency_icon': currency_icon,
        })

    def trading_logout_page(self, request):
        return render(request,"digital-investment/logout.html")

    def trading_forgot_pin(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        return render(request,"digital-investment/forgot-pin.html")
    
    def trading_verify_otp(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')
        
        return render(request,"digital-investment/verify-otp.html")
    
    def trading_reset_pin(self, request):
        if request.trading_error:
            return redirect('digital_gateway')

        customer = request.trading_customer
        if not customer:
            return redirect('digital_gateway')

        return render(request,"digital-investment/reset-pin.html")
        
class TradingOnboard:
    def saveCutomerBankDetails(self,request):
        if request.method == 'POST':
            try:
                # ================= CUSTOMER VALIDATION =================
                if request.trading_error:
                    return JsonResponse({'success':'0','message':request.trading_error}, status=status.HTTP_200_OK)
                
                customer = request.trading_customer
                
                # ================= VALIDATION =================
                
                errors = {}

                rules = {
                    "bank_name": (r"^[A-Za-z.&\s]+$", "Please input alphabet characters only."),
                    "account_holder_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                    "account_number": (r"^[0-9]+$", "Please enter a valid account number."),
                    "ifsc_code": (r"^[A-Za-z]{4}0[A-Z0-9a-z]{6}$", "Please enter valid IFSC code"),
                    "branch_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                }

                required_fields = [
                    "account_holder_name",
                    "account_number", "ifsc_code"
                ]

                # ================= REQUIRED FIELD CHECK =================
                for field in required_fields:
                    if not request.POST.get(field):
                        errors[field] = "This field is required"

                # ================= PATTERN VALIDATION =================
                for field, (pattern, msg) in rules.items():
                    value = request.POST.get(field, "").strip()
                    if value and not re.match(pattern, value):
                        errors[field] = msg

                # ================= FILE VALIDATION =================
                # allowed_ext = (".pdf", ".doc", ".docx", ".ppt", ".pptx")
                # required_files = ["cancelled_cheque", "passbook", "bank_statement"]
                allowed_ext = (".jpg", ".jpeg", ".png", ".pdf")
                max_file_size = 5 * 1024 * 1024  # 5MB
                allowed_mime = ["image/jpeg","image/png","application/pdf"]
                
                # required_files = ["cancelled_cheque", "passbook"]
                # for file_field in required_files:
                #     f = request.FILES.get(file_field)

                #     if not f:
                #         errors[file_field] = "This document is required"
                #         continue

                #     # ===== EXTENSION VALIDATION =====
                #     if not f.name.lower().endswith(allowed_ext):
                #         errors[file_field] = "Only JPG, PNG and PDF files are allowed"
                #         continue

                #     if f.content_type not in allowed_mime:
                #         errors[file_field] = "Invalid file type"
                #         continue

                #     # ===== FILE SIZE VALIDATION =====
                #     if f.size > max_file_size:
                #         errors[file_field] = "File size should not exceed 5MB"
                #         continue

                cancelled_cheque = request.FILES.get("cancelled_cheque")
                passbook = request.FILES.get("passbook")
                aadhaar_front = request.FILES.get("aadhaar_front")
                aadhaar_back = request.FILES.get("aadhaar_back")
                pan_front = request.FILES.get("pan_front")
                pan_back = request.FILES.get("pan_back")

                # ===== AT LEAST ONE BANK DOCUMENT REQUIRED =====
                if not cancelled_cheque and not passbook:
                    errors["file_error"] = "Upload Cancelled Cheque or Passbook"

                # ===== AADHAAR REQUIRED =====
                if not aadhaar_front:
                    errors["aadhaar_front"] = "Aadhaar front photo is required"
                if not aadhaar_back:
                    errors["aadhaar_back"] = "Aadhaar back photo is required"

                # ===== PAN REQUIRED =====
                if not pan_front:
                    errors["pan_front"] = "PAN front photo is required"
                if not pan_back:
                    errors["pan_back"] = "PAN back photo is required"

                files_to_validate = {
                    "cancelled_cheque": cancelled_cheque,
                    "passbook": passbook,
                    "aadhaar_front": aadhaar_front,
                    "aadhaar_back": aadhaar_back,
                    "pan_front": pan_front,
                    "pan_back": pan_back,
                }

                for field_name, f in files_to_validate.items():

                    if not f:
                        continue

                    if not f.name.lower().endswith(allowed_ext):
                        errors[field_name] = "Only JPG, PNG and PDF files are allowed"
                        continue

                    if f.content_type not in allowed_mime:
                        errors[field_name] = "Invalid file type"
                        continue

                    if f.size > max_file_size:
                        errors[field_name] = "File size should not exceed 5MB"
                        continue

                # ================= FINAL RESPONSE =================
                if errors:
                    return JsonResponse({'success':'2','message':'Validation errors',"errors": errors}, status=status.HTTP_200_OK)
                
                # ================= FETCH FORM DATA =================
                bank_name = request.POST.get("bank_name")
                account_holder_name = request.POST.get("account_holder_name")
                account_number = request.POST.get("account_number")
                ifsc_code = request.POST.get("ifsc_code")
                branch_name = request.POST.get("branch_name")

                # ================= GENERATE UNIQUE IDS =================
                bank_unique_id = random_obj.generateUID()

                with transaction.atomic():
                    # ================= BANK DETAILS =================
                    CustomerTradingBankDetails.objects.create(
                        customer=customer,
                        unique_id=bank_unique_id,
                        date=current_date,
                        bank_name=bank_name,
                        account_holder_name=account_holder_name,
                        account_number=account_number,
                        ifsc_code=ifsc_code,
                        branch_name=branch_name
                    )

                    # ================= DOCUMENTS =================
                    base_dir = os.path.join(settings.MEDIA_ROOT, f"customer-documents/{customer.unique_id}/")
                    os.makedirs(base_dir, exist_ok=True)

                    documents = {
                        "cancelled_cheque": ("BANK_CHEQUE", "cancelled_cheque"),
                        "passbook": ("BANK_PASSBOOK", "passbook"),
                        "aadhaar_front": ("AADHAAR", "aadhaar_front"),
                        "aadhaar_back": ("AADHAAR", "aadhaar_back"),
                        "pan_front": ("PAN", "pan_front"),
                        "pan_back": ("PAN", "pan_back"),
                    }

                    for field_name, (doc_type, file_prefix) in documents.items():
                        file_obj = request.FILES.get(field_name)
                        if not file_obj:
                            continue

                        file_name = util_obj.save_document(file_obj, base_dir, file_prefix)

                        CustomerTradingDocuments.objects.create(
                            customer=customer,
                            unique_id=random_obj.generateUID(),
                            date=current_date,
                            doc_type=doc_type,
                            file_path=f"customer-documents/{customer.unique_id}/{file_name}"
                        )

                    return JsonResponse({
                        "success": 1,
                        "message": "Bank details submitted successfully",
                        "redirectURL": reverse('digital_gateway')
                    })
            except Exception as e:
                return JsonResponse({
                    "success": 0,
                    "message": "Something went wrong",
                    "error": str(e)
                }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                    "success": 0,
                    "message": "Something went wrong"
                }, status=status.HTTP_200_OK)
        
    def saveCutomerTermsDetails(self,request):
        if request.method == 'POST':
            try:
                # ================= CUSTOMER VALIDATION =================
                if request.trading_error:
                    return JsonResponse({'success':'0','message':request.trading_error}, status=status.HTTP_200_OK)
                
                customer = request.trading_customer
                
                # ================= FETCH FORM DATA =================
                accept = request.POST.get('accept_terms')

                # ================= GENERATE UNIQUE IDS =================
                unique_id = random_obj.generateUID()
                ip = util_obj.getIPAddress(request)
                
                # ================= VALIDATION =================
                errors = {}

                if accept != 'Yes':
                    errors['accept_terms'] =  'Please accept terms & conditions'

                # ================= FINAL RESPONSE =================
                if errors:
                    return JsonResponse({'success':'2','message':'Validation errors',"errors": errors}, status=status.HTTP_200_OK)
                
                with transaction.atomic():
                    if CustomerTradingTerms.objects.filter(customer=customer).exists():
                        return JsonResponse({
                            'success': 1,
                            'message': 'Terms already accepted',
                            "redirectURL": reverse('digital_gateway')
                        })
                    
                    CustomerTradingTerms.objects.create(
                        customer=customer,
                        accepted='Yes',
                        accepted_date=current_date,
                        accepted_ip=ip,
                        version='1'
                    )

                    # 5️⃣ Redirect to pending approval
                    return JsonResponse({
                        'success': 1,
                        'message': 'Terms accepted successfully',
                        "redirectURL": reverse('digital_gateway')
                    })
            except Exception as e:
                return JsonResponse({
                    "success": 0,
                    "message": "Something went wrong",
                    "error": str(e)
                }, status=status.HTTP_200_OK)
        else:
            return JsonResponse({
                    "success": 0,
                    "message": "Something went wrong"
                }, status=status.HTTP_200_OK)
        
    def update_trading_status(self, request):
        if request.method != 'POST':
            return JsonResponse({'success': 0, 'message': 'Invalid request method'})

        customer_uid = request.POST.get('customer_id')
        status_value = request.POST.get('status')  # Approved / Rejected

        # ✅ BASIC VALIDATION
        if not customer_uid:
            return JsonResponse({'success': 0, 'message': 'Invalid customer ID'})

        if status_value not in ['Approved', 'Rejected']:
            return JsonResponse({'success': 0, 'message': 'Invalid status value'})

        try:
            with transaction.atomic():
                customer = Customer.objects.select_for_update().get(
                    unique_id=customer_uid
                )

                trading_account = CustomerTradingAccount.objects.select_for_update().filter(
                    customer=customer,
                    trading_enabled='ON',
                    is_blocked='No'
                ).first()

                if not trading_account:
                    return JsonResponse({
                        'success': 0,
                        'message': 'Digital investment account not found'
                    })

                # ❗ SAME STATUS CHECK
                if trading_account.status == status_value:
                    return JsonResponse({
                        'success': 0,
                        'message': 'No changes detected'
                    })

                # 🔄 UPDATE STATUS
                trading_account.status = status_value
                trading_account.approved_date = current_date
                trading_account.approved_by = request.session.get('login_id')
                trading_account.save(update_fields=[
                    'status', 'approved_date', 'approved_by'
                ])

                # Note : No need to do this step bcoz we are doing OTT and JWT SSO Authentication 
                
                # # ✅ APPROVED CASE
                # if status_value == 'Approved':
                    # # 🔐 Generate password
                    # raw_password = random_obj.generate_short_uuid(10)
                    # salt, hashed_password = encrypt_obj.runEncryprion(raw_password)

                    # # 🧾 Create login if not exists
                    # login, created = CustomerTradingLogin.objects.get_or_create(
                    #     customer=customer,
                    #     defaults={
                    #         'trading_password': hashed_password,
                    #         'salt': salt,
                    #         'password_text': raw_password,
                    #         'last_login_ip': util_obj.getIPAddress(request)
                    #     }
                    # )

                    # # 📧 Send mail (only first time)
                    # if created:
                    #     mail_obj.welcomeMessage(
                    #         customer.name,
                    #         customer.email,
                    #         customer.mobile,
                    #         raw_password
                    #     )

                return JsonResponse({
                    'success': 1,
                    'message': f'Digital investment account {status_value} successfully'
                })

        except Customer.DoesNotExist:
            return JsonResponse({'success': 0, 'message': 'Customer not found'})

        except Exception:
            return JsonResponse({'success': 0, 'message': 'Something went wrong'})
        
    def getTradingDetails(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('trading_details') is not None:
                        unique_id = request.POST.get("unique_id", "").strip()

                        if not unique_id:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                            
                        digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                        if digit_validate != 1:
                            return util_obj.printErrorResponse_200(digit_validate)

                        customer = Customer.objects.filter(unique_id=unique_id).first()

                        if not customer:
                            return util_obj.printErrorResponse_200('Data not found!')
                        
                        tradingDetails = self.getTradingDataDetails(customer.unique_id,include_bank=True,include_docs=True)
                                    
                        data = {'success':'1', 'tradingDetails':tradingDetails}
                                
                        return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
                    
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                
                except Exception as e:
                    # print("getUser error:", e)
                    
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            
            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        
        return util_obj.goToLogin(request)
    
    def getTradingDataDetails(self, customer_unique_id, include_bank=False, include_docs=False):
        result = {}

        if include_bank:
            bank_qs = CustomerTradingBankDetails.objects.filter(
                customer__unique_id=customer_unique_id
            )

            result["bank_details"] = [{
                'sr_no': i + 1,
                'unique_id': row.unique_id,
                'bank_name': row.bank_name,
                'account_holder_name': row.account_holder_name,
                'account_number': row.account_number,
                'ifsc_code': row.ifsc_code,
                'branch_name': row.branch_name,
                'date': timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
            } for i, row in enumerate(bank_qs)]

        if include_docs:
            doc_qs = CustomerTradingDocuments.objects.filter(
                customer__unique_id=customer_unique_id
            )

            result["documents"] = [{
                'sr_no': i + 1,
                'unique_id': row.unique_id,
                'doc_type': row.doc_type,
                'file_path': urlPrefix + row.file_path,
                'date': timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
            } for i, row in enumerate(doc_qs)]

        return result
    
class TradingAuth:
    # def trading_login(self, request):
    #     if request.method != 'POST':
    #         return JsonResponse({'success': 0, 'message': 'Invalid request'})

    #     username = request.POST.get('username')  # mobile
    #     password = request.POST.get('password')

    #     if not username or not password:
    #         return JsonResponse({'success': 0, 'message': 'All fields are required'})

    #     # ✅ mobile validation
    #     if valid_obj.validate_mobile(username) != 1:
    #         return JsonResponse({'success': 0, 'message': 'Invalid mobile number'})

    #     # ✅ customer check
    #     customer = Customer.objects.filter(
    #         mobile=username,
    #         trading='ON',
    #         access='Granted'
    #     ).first()

    #     if not customer:
    #         return JsonResponse({'success': 0, 'message': 'Digital investment access not available'})

    #     # ✅ trading account check
    #     trading_account = CustomerTradingAccount.objects.filter(
    #         customer=customer,
    #         trading_enabled='ON',
    #         is_blocked='No',
    #         status='Approved'
    #     ).first()

    #     if not trading_account:
    #         return JsonResponse({'success': 0, 'message': 'Digital investment approval pending'})

    #     # ✅ trading login table
    #     login = CustomerTradingLogin.objects.filter(customer=customer).first()
    #     if not login:
    #         return JsonResponse({'success': 0, 'message': 'Digital investment login not found'})

    #     # ✅ password verify
    #     encrypted_pass = encrypt_obj.encryption(login.salt, password)
    #     if encrypted_pass != login.trading_password:
    #         return JsonResponse({'success': 0, 'message': 'Invalid username or password'})

    #     # ✅ SUCCESS
    #     session_id = random_obj.generateUID()
    #     ip_address = util_obj.getIPAddress(request)
    #     user_agent = request.META.get('HTTP_USER_AGENT', '')

    #     with transaction.atomic():
    #         CustomerTradingLoginReport.objects.create(
    #             trading_account=trading_account,
    #             login_ip=ip_address,
    #             user_agent=user_agent,
    #             session_id=session_id,
    #             login_type='Web'  # ya 'Mobile', agar app se login ho raha ho
    #         )

    #         request.session['customer_id'] = customer.id
    #         request.session['customer_uid'] = customer.unique_id
    #         request.session['trading_logged'] = True
    #         request.session['session_id'] = session_id

    #     return JsonResponse({
    #         'success': 1,
    #         'message': 'Login successful',
    #         'redirect': 'digital-dashboard/?cid=14214894724756354195'
    #     })

    def handle_pin_action(self, request):
        customer = request.trading_customer
        validated_token = request.validated_token

        if request.trading_error:
            return JsonResponse({'success':'0','message':request.trading_error}, status=status.HTTP_200_OK)

        mode = request.POST.get('mode')
        pin = request.POST.get('pin')
        confirm_pin = request.POST.get('confirm_pin')

        if not customer or not validated_token:
            return JsonResponse({'success': 0, 'message': 'Session expired'})
        
        if mode not in ['setup', 'verify']:
            return JsonResponse({'success': 0, 'message': 'Invalid request'})

        if not pin or len(pin) != 6 or not pin.isdigit():
            return JsonResponse({'success': 0, 'message': 'Invalid PIN format'})

        login_entry, _ = CustomerTradingLogin.objects.get_or_create(customer=customer)

        now = timezone.now()

        # 🔥 RESET IF LOCK EXPIRED
        if login_entry.lock_until and login_entry.lock_until <= now:
            login_entry.wrong_attempts = 0
            login_entry.lock_until = None
            login_entry.save()

        # 🔒 ACTIVE LOCK CHECK
        if login_entry.lock_until and login_entry.lock_until > now:
            return JsonResponse({
                'success': 0,
                'locked_until': login_entry.lock_until,
                'message': 'Account locked'
            })

        try:
            with transaction.atomic():

                # ================= SETUP MODE =================
                if mode == 'setup':

                    if not confirm_pin:
                        return JsonResponse({'success': 0, 'message': 'Confirm PIN required'})

                    if pin != confirm_pin:
                        return JsonResponse({'success': 0, 'message': 'PIN mismatch'})

                    salt, hash_pin = encrypt_obj.runEncryprion(pin)

                    login_entry.pin_salt = salt
                    login_entry.pin_hash = hash_pin
                    login_entry.pin_set = True
                    login_entry.wrong_attempts = 0
                    login_entry.lock_until = None
                    login_entry.pin = pin
                    login_entry.save()

                # ================= VERIFY MODE =================
                encrypted_attempt = encrypt_obj.encryption(login_entry.pin_salt, pin)

                if encrypted_attempt != login_entry.pin_hash:

                    login_entry.wrong_attempts += 1

                    # 🔒 If 5th wrong attempt → LOCK
                    if login_entry.wrong_attempts >= 5:

                        # login_entry.lock_until = now + datetime.timedelta(minutes=15)
                        # Use exponential lock: Use exponential lock:
                        lock_multiplier = login_entry.wrong_attempts - 4
                        lock_minutes = min(15 * lock_multiplier, 60)
                        login_entry.lock_until = now + datetime.timedelta(minutes=lock_minutes)
                        login_entry.save()

                        # 🔎 Audit Log
                        CustomerTradingLoginReport.objects.create(
                            trading_account=customer.customertradingaccount,
                            login_ip=util_obj.getIPAddress(request),
                            user_agent=request.META.get("HTTP_USER_AGENT", ""),
                            login_type="WEB",
                            status="LOCKED"
                        )

                        return JsonResponse({
                            'success': 0,
                            'locked_until': login_entry.lock_until,
                            'message': 'Account locked for 15 minutes'
                        })

                    # ❌ Normal Wrong Attempt (Less than 5)
                    login_entry.save()

                    CustomerTradingLoginReport.objects.create(
                        trading_account=customer.customertradingaccount,
                        login_ip=util_obj.getIPAddress(request),
                        user_agent=request.META.get("HTTP_USER_AGENT", ""),
                        login_type="WEB",
                        status="FAILED"
                    )

                    return JsonResponse({
                        'success': 0,
                        'attempts_remaining': 5 - login_entry.wrong_attempts,
                        'message': 'Invalid PIN'
                    })

                # ================= SUCCESS =================
                login_entry.wrong_attempts = 0
                login_entry.lock_until = None
                login_entry.last_login = now
                login_entry.last_login_ip = util_obj.getIPAddress(request)
                login_entry.save()

                # 🔎 Success Audit
                CustomerTradingLoginReport.objects.create(
                    trading_account=customer.customertradingaccount,
                    login_ip=util_obj.getIPAddress(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    login_type="WEB",
                    status="SUCCESS"
                )

                # # ================= JWT UPGRADE =================
                # refresh_token_str = request.COOKIES.get('refresh_token')
                # if not refresh_token_str:
                #     return JsonResponse({'success': 0, 'message': 'Session expired'})

                # try:
                #     refresh = RefreshToken(refresh_token_str)
                # except Exception:
                #     return JsonResponse({'success': 0, 'message': 'Session expired'})

                # # Re-add required claims
                # refresh['customer_uid'] = customer.unique_id
                # refresh['trading_access'] = True
                # refresh['is_pin_verified'] = True

                # access_token = str(refresh.access_token)
                # refresh_token = str(refresh)

                # # 🔥 CRITICAL FIX: GENERATE NEW TOKENS
                # refresh = RefreshToken.for_user(customer)

                # refresh["customer_uid"] = customer.unique_id
                # refresh["mobile"] = customer.mobile
                # refresh["trading_access"] = True
                # refresh["device_id"] = validated_token.get("device_id")
                # refresh["ip"] = validated_token.get("ip")
                # refresh["app_version"] = validated_token.get("app_version")

                # access_token = refresh.access_token
                # access_token["is_pin_verified"] = True
                # refresh_token = str(refresh)

                # 🔐 Set Sliding PIN Session
                pin_key = cust_util_obj.get_pin_cache_key(customer.id)
                cache.set(pin_key, True, timeout=settings.PIN_TTL_SECONDS)

                response = JsonResponse({
                    'success': 1,
                    'redirect': reverse('digital_dashboard')
                })

                # response.set_cookie(
                #     'access_token',
                #     access_token,
                #     httponly=True,
                #     secure=True,
                #     samesite='Strict',
                #     max_age=900
                # )

                # response.set_cookie(
                #     'refresh_token',
                #     refresh_token,
                #     httponly=True,
                #     secure=True,
                #     samesite='Strict',
                #     max_age=604800
                # )

                return response

        except Exception as e:
            return JsonResponse({
                'success': 0,
                'message': 'Something went wrong'
            })

    @require_trading_auth
    def trading_logout(self, request):
        if request.trading_error:
            return redirect("digital_gateway")

        customer = request.trading_customer
        validated_token = request.validated_token

        try:
            if customer:

                # 🔐 Remove PIN verification cache
                cache.delete(cust_util_obj.get_pin_cache_key(customer.id))

                # 🔐 Remove active OTT pointer
                cache.delete(f"USER_ACTIVE_OTT:{customer.id}")

                # 🔐 Optional: invalidate JWT session cache
                jti = validated_token.get("jti")
                if jti:
                    cache.set(f"JWT_LOGOUT:{jti}", True, timeout=900)

        except Exception:
            pass

        response = redirect("trading_logout_page")

        response.delete_cookie("access_token", path="/")
        response.delete_cookie("refresh_token", path="/")

        response["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response["Pragma"] = "no-cache"
        response["Expires"] = "0"

        return response

    @require_trading_auth
    def trading_profile(self, request):
        obj = ProfileUtil()
        if request.trading_error:
            return redirect("digital_gateway")

        customer = request.trading_customer
        if not customer:
            return redirect("digital_gateway")

        # 1️⃣ Address (multiple)
        addresses = CustomerAddress.objects.filter(
            customer=customer.unique_id,
            access="Granted"
        ).order_by("-date")

        # 2️⃣ Trading account
        trading_account = (
            CustomerTradingAccount.objects
            .select_related("ra")
            .filter(customer=customer)
            .first()
        )

        # 3️⃣ Bank details
        bank = CustomerTradingBankDetails.objects.filter(
            customer=customer
        ).first()

        # 4️⃣ Documents
        documents_qs = CustomerTradingDocuments.objects.filter(
            customer=customer
        )

        documents = {
            "AADHAAR": None,
            "PAN": None,
            "BANK_CHEQUE": None,
            "BANK_PASSBOOK": None,
            "BANK_STATEMENT": None
        }

        for doc in documents_qs:
            documents[doc.doc_type] = urlPrefix+doc.file_path

        # 5️⃣ Terms
        terms = CustomerTradingTerms.objects.filter(
            customer=customer
        ).first()

        # 6️⃣ Login info (optional)
        login_info = CustomerTradingLogin.objects.filter(
            customer=customer
        ).first()

        # 7️⃣ Masked values
        aadhaar_masked = obj.mask_aadhaar(customer.aadhaar_number)
        pan_masked = obj.mask_pan(customer.pan_number)
        ip_masked = obj.mask_ip(login_info.last_login_ip)

        account_masked = None
        if bank:
            account_masked = obj.mask_account(bank.account_number)

        context = {
            "customer": customer,
            "addresses": addresses,
            "trading_account": trading_account,
            "bank": bank,
            "documents": documents,
            "terms": terms,
            "login_info": login_info,
            "aadhaar_masked": aadhaar_masked,
            "pan_masked": pan_masked,
            "account_masked": account_masked,
            "ip_masked" : ip_masked
        }

        return render(request,"digital-investment/profile.html",context)

class TradingPinRecovery:
    @require_trading_auth
    def send_pin_otp(self, request):
        if request.trading_error:
            return JsonResponse({"success": 0,"message": request.trading_error})

        customer = request.trading_customer
        validated_token = request.validated_token

        try:
            # 🔒 DEVICE CHECK
            if validated_token.get("device_id") != customer.unique_application_id:
                return JsonResponse({"success": 0,"message": "Device mismatch"})

            # 🔒 RATE LIMIT (1 OTP / 60 sec)
            rate_key = PinResetKeys.rate(customer.id)

            if cache.get(rate_key):
                return JsonResponse({"success": 0,"message": "Please wait before requesting OTP again"})

            # 🔑 GENERATE OTP
            otp = str(secrets.randbelow(1000000)).zfill(6)

            salt, otp_hash = encrypt_obj.runEncryprion(otp)

            payload = {
                "hash": otp_hash,
                "salt": salt,
                "created": timezone.now().isoformat(),
                "version": secrets.token_hex(4)
            }

            # Store OTP in cache
            cache.set(PinResetKeys.otp(customer.id),payload,timeout=300)

            # Rate limit
            cache.set(rate_key, True, timeout=60)

            # reset attempts
            cache.delete(PinResetKeys.attempts(customer.id))

            # 🔔 SEND EMAIL
            try:
                mail_obj.send_otp(customer.name, customer.email, otp)
            except Exception:
                cache.delete(PinResetKeys.otp(customer.id))
                return JsonResponse({
                    "success":0,
                    "message":"Unable to send OTP"
                })

            CustomerTradingLoginReport.objects.create(
                trading_account=customer.customertradingaccount,
                login_ip=util_obj.getIPAddress(request),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
                login_type="WEB",
                status="OTP_SENT"
            )

            return JsonResponse({
                "success": 1,
                "message": "OTP sent successfully",
                "redirectURL": reverse("trading_verify_otp"),
                "otp_version": payload["version"]
            })

        except Exception:
            return JsonResponse({"success": 0,"message": "Unable to send OTP"})
        
    @require_trading_auth
    def verify_pin_otp(self, request):
        if request.method != "POST":
            return JsonResponse({
                "success":0,
                "message":"Invalid request"
            })
        
        if request.trading_error:
            return JsonResponse({"success":0,"message":request.trading_error})

        otp = request.POST.get("otp","").strip()

        if not otp or len(otp) != 6:
            return JsonResponse({
                "success":0,
                "message":"Invalid OTP"
            })

        customer = request.trading_customer

        lock_key = None

        try:

            lock_key = f"PIN_VERIFY_LOCK:{customer.id}"

            if cache.get(lock_key):
                return JsonResponse({
                    "success":0,
                    "message":"Processing request"
                })

            cache.set(lock_key,True,timeout=5)

            if cache.get(PinResetKeys.lock(customer.id)):
                return JsonResponse({
                    "success":0,
                    "locked":True,
                    "message":"Too many attempts. Try later."
                })

            payload = cache.get(PinResetKeys.otp(customer.id))

            # OTP expired
            if not payload:
                return JsonResponse({
                    "success":0,
                    "otp_expired":True,
                    "message":"OTP expired"
                })

            created_time = datetime.datetime.fromisoformat(payload["created"])

            if timezone.now() - created_time > datetime.timedelta(minutes=5):

                cache.delete(PinResetKeys.otp(customer.id))

                return JsonResponse({
                    "success":0,
                    "otp_expired":True,
                    "message":"OTP expired"
                })

            encrypted = encrypt_obj.encryption(
                payload["salt"],
                otp
            )

            if encrypted != payload["hash"]:

                time.sleep(random.uniform(0.8,1.5))

                attempts = cache.get(PinResetKeys.attempts(customer.id),0) + 1
                cache.set(PinResetKeys.attempts(customer.id),attempts,timeout=300)

                if attempts >= 5:

                    cache.set(
                        PinResetKeys.lock(customer.id),
                        True,
                        timeout=600
                    )

                    return JsonResponse({
                        "success":0,
                        "locked":True,
                        "message":"Too many attempts"
                    })

                return JsonResponse({
                    "success":0,
                    "attempts_remaining":5-attempts,
                    "message":"Invalid OTP"
                })

            # SUCCESS
            cache.delete(PinResetKeys.otp(customer.id))
            cache.delete(PinResetKeys.attempts(customer.id))
            cache.delete(PinResetKeys.lock(customer.id))

            cache.set(
                PinResetKeys.session(customer.id),
                True,
                timeout=300
            )

            CustomerTradingLoginReport.objects.create(
                trading_account=customer.customertradingaccount,
                login_ip=util_obj.getIPAddress(request),
                user_agent=request.META.get("HTTP_USER_AGENT",""),
                login_type="WEB",
                status="OTP_SUCCESS"
            )

            return JsonResponse({
                "success":1,
                "redirectURL":reverse("trading_reset_pin")
            })
        finally:
            if lock_key:
                cache.delete(lock_key)
        
    @require_trading_auth
    def reset_trading_pin(self, request):
        if request.method != "POST":
            return JsonResponse({
                "success":0,
                "message":"Invalid request"
            })
        
        if request.trading_error:
            return JsonResponse({
                "success": 0,
                "message": request.trading_error
            })

        customer = request.trading_customer

        pin = request.POST.get("pin")
        confirm_pin = request.POST.get("confirm_pin")

        if not pin or not confirm_pin:
            return JsonResponse({
                "success": 0,
                "message": "PIN required"
            })

        if pin != confirm_pin:
            return JsonResponse({
                "success": 0,
                "message": "PIN mismatch"
            })

        if not pin.isdigit() or len(pin) != 6:
            return JsonResponse({
                "success": 0,
                "message": "Invalid PIN format"
            })
        
        if pin in ["000000","111111","123456","654321"]:
            return JsonResponse({
                "success":0,
                "message":"Weak PIN not allowed"
            })

        # 🔒 SESSION CHECK
        if not cache.get(PinResetKeys.session(customer.id)):
            return JsonResponse({
                "success":0,
                "session_expired":True,
                "message":"Session expired"
            })

        try:
            with transaction.atomic():

                login_entry = CustomerTradingLogin.objects.select_for_update().get(customer=customer)

                salt, hash_pin = encrypt_obj.runEncryprion(pin)

                login_entry.pin_hash = hash_pin
                login_entry.pin_salt = salt
                login_entry.pin = pin
                login_entry.wrong_attempts = 0
                login_entry.lock_until = None
                login_entry.save()

                cache.delete(PinResetKeys.session(customer.id))

                CustomerTradingLoginReport.objects.create(
                    trading_account=customer.customertradingaccount,
                    login_ip=util_obj.getIPAddress(request),
                    user_agent=request.META.get("HTTP_USER_AGENT", ""),
                    login_type="WEB",
                    status="PIN_RESET"
                )

            return JsonResponse({
                "success": 1,
                "message": "PIN reset successful",
                "redirectURL": reverse("digital_gateway")
            })

        except Exception as e:
            return JsonResponse({
                "success": 0,
                "message": "Unable to reset PIN"
            })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def checkCustomerTradingAccess(request):
    if request.method == 'POST':
        try:
            field = request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                customer = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id).first()
                if customer:
                    if customer.access=='Granted' and customer.trading=='ON':
                        return Response({'success':'1', 'trading':'ON'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0', 'trading':'OFF', 'message':'You are blocked by the administation. Kindly contact company manager for more details!'}, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data available for this user!'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def initiate_trading_handshake(request):
    try:
        cid = request.data.get("user_unique_id", "").strip()
        device_id = request.data.get("device_id", "").strip()
        app_version = request.data.get("app_version", "").strip()

        if not cid or not device_id or not app_version:
            return Response({"success": "0","message": "Missing required parameters."}, status=200)

        # Step 1: Verify Customer
        trading_account = cust_util_obj.get_valid_trading_customer(cid)
        if not trading_account:
            return Response({"success": "0", "message": "Trading account not active"}, status=200)
        
        customer = trading_account.customer
        if not customer:
            return Response({'success': '0', 'message': 'Digital Investment access is disabled.'}, status=200)

        # Step 2: Device match
        if device_id != customer.unique_application_id:
            return Response({'success': '0', 'message': 'Device identification failed.'}, status=200)

        # Step 3: Trading account check
        # trading_account = CustomerTradingAccount.objects.filter(
        #     customer=customer,
        #     trading_enabled='ON',
        #     is_blocked='No'
        # ).first()

        # if not trading_account:
        #     return Response({"success": "0", "message": "Trading account not active"}, status=200)

        # Step 4: Rate limit
        rate_key = f"HANDSHAKE_RATE:{customer.id}"
        count = cache.get(rate_key)
        if (count or 0) >= 5:
            return Response({"success": "0", "message": "Too many attempts."}, status=200)

        cache.set(rate_key, (count or 0) + 1, timeout=60)

        # Step 5: Remove previous active OTT
        previous_key = f"USER_ACTIVE_OTT:{customer.id}"
        old_ott = cache.get(previous_key)
        # print(old_ott)
        if old_ott:
            cache.delete(f"OTT:{old_ott}")

        # Step 6: Generate OTT
        ott = secrets.token_urlsafe(32)
        cache_key = f"OTT:{ott}"
        # print(ott)
        payload = {
            "customer_id": customer.id,
            "customer_uid": customer.unique_id,
            "device_id": device_id,
            "ip": util_obj.getIPAddress(request),
            "app_version": app_version
        }

        cache.set(cache_key, payload, settings.OTT_TTL_SECONDS)
        cache.set(previous_key, ott, settings.OTT_TTL_SECONDS)

        host_url = request.build_absolute_uri('/')
        bridge_url = f"{host_url}digital-investment/bridge?token={ott}&device_id={device_id}"

        return Response({
            'success': '1',
            'exchange_token': ott,
            'expires_in': settings.OTT_TTL_SECONDS,
            'bridge_url': bridge_url
        }, status=200)
    except Exception as e:
        return Response({'success': '0','message': 'Internal server error during handshake.'}, status=500)