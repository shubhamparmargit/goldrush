from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utility.views import Utility, RandomIdGenerate, Validation, Encryption, current_date, imageType_lst, urlPrefix, domainURL
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
import os, random
from django.conf import settings
from customer.models import Customer, CustomerAddress, CustomerLoginReport, PasswordResetRequest
from users.models import Franchise
from django.core.files.storage import default_storage
from datetime import datetime, timedelta
from django.utils import timezone
import uuid
from messaging_hub.views import MailNotification

mail_obj = MailNotification()
util_obj = Utility()
random_obj = RandomIdGenerate()
valid_obj = Validation()
encrypt_obj = Encryption()

class CustomerData:
    def verifyCustomer(self, mobile, user_unique_id):
        try:
            if mobile != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
    def getCustomer(self, login_success):
        data = []
        if login_success:
            register_date_time = timezone.localtime(login_success.date).strftime('%d-%m-%Y @ %I:%M %p')
            addressList = self.getCustomerAddressList(login_success.unique_id)

            last_login = CustomerLoginReport.objects.filter(customer=login_success.unique_id).only('login_date_time','latitude','longitude').order_by('-login_date_time').first()

            last_login_date_time = ''
            latitude = ''
            longitude = ''

            if last_login:
                last_login_date_time = timezone.localtime(last_login.login_date_time).strftime('%d-%m-%Y @ %I:%M %p')
                latitude = last_login.latitude
                longitude = last_login.longitude
            
            data.append({'success':'1','register_date_time':register_date_time, 'unique_id':login_success.unique_id, 'name':login_success.name, 'aadhaar_number':login_success.aadhaar_number, 'aadhaar_front_image':urlPrefix+login_success.aadhaar_front_image, 'aadhaar_back_image':urlPrefix+login_success.aadhaar_back_image, 'pan_number':login_success.pan_number, 'pan_front_image':urlPrefix+login_success.pan_front_image, 'mobile':login_success.mobile, 'email':login_success.email, 'referral_code':login_success.referral_code, 'address_details':addressList, 'last_login_date_time': last_login_date_time, 'latitude': latitude, 'longitude': longitude})
        return data

    def getCustomerAddressList(self, user_unique_id):
        obj = CustomerAddress.objects.filter(access = 'Granted', customer__unique_id = user_unique_id)
        data = []
        if obj:
            sr_no = 1
            for row in obj:
                date = timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')

                data.append({'sr_no':sr_no, 'unique_id':row.unique_id, 'name':row.name, 'mobile':row.mobile, 'pincode':row.pincode, 'postoffice':row.postoffice, 'state':row.state, 'city':row.city, 'district':row.district, 'region':row.region, 'address_line_1':row.address_line_1, 'address_line_2':row.address_line_2, 'date':date})
                sr_no += 1
        return data
    
    def validate_reset_link(self, request):
        unique_id = request.GET.get('id')
        model_class = PasswordResetRequest
        context = util_obj.generic_reset_link_validation(model_class, unique_id)
        return render(request, 'portal/set-password.html', {'context': context})

custObj = CustomerData()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def customerRegistarion(request):

    if request.method != 'POST':
        return Response({'success': '0', 'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)

    try:

        # ================= GET DATA =================
        field = request.POST.get('field', '')
        name = request.POST.get('name', '').strip()
        aadhaar_number = request.POST.get('aadhaar_number', '').strip() or None
        pan_number = request.POST.get('pan_number', '').strip() or None
        mobile = request.POST.get('mobile', '').strip()
        email = None
        password_text = request.POST.get('password', '').strip()
        referral_code = request.POST.get('referral_code', '').strip() or None

        pincode = request.POST.get('pincode', '').strip() or None
        postoffice = request.POST.get('postoffice', '').strip() or None
        state = request.POST.get('state', '').strip() or None
        city = request.POST.get('city', '').strip() or None
        district = request.POST.get('district', '').strip() or None
        region = request.POST.get('region', '').strip() or None

        address_line_1 = request.POST.get('address_line_1', '').strip() or None
        address_line_2 = request.POST.get('address_line_2', '').strip() or None

        latitude = float(request.POST.get('latitude') or 0.0)
        longitude = float(request.POST.get('longitude') or 0.0)
        location = request.POST.get('location', '').strip() or None

        aadhaar_front_image = request.FILES.get('aadhaar_front_image')
        aadhaar_back_image = request.FILES.get('aadhaar_back_image')
        pan_front_image = request.FILES.get('pan_front_image')

        # ================= BASIC REQUIRED CHECK =================
        # Minimal required fields for registration: name, mobile, password, referral_code
        if field != "" or not all([name, mobile, password_text, referral_code]):
            return Response({'success': '0', 'message': 'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)

        # ================= VALIDATION =================
        # Validate only provided fields
        valid_obj.validate_alpha_multiple_keys(name=name)

        address_components = {}
        if postoffice: address_components["postoffice"] = postoffice
        if state: address_components["state"] = state
        if city: address_components["city"] = city
        if region: address_components["region"] = region
        if district: address_components["district"] = district
        if address_components:
            valid_obj.validate_address_component_multiple_keys(**address_components)

        if aadhaar_number:
            valid_obj.validate_aadhaar_verhoeff(aadhaar_number)
        if pan_number:
            valid_obj.validate_pan_entity(pan_number)
            
        valid_obj.validate_mobile_number(mobile)
        
        valid_obj.validate_password(password_text)
        
        if pincode:
            valid_obj.validate_pincode(pincode)

        if address_line_1 or address_line_2:
            valid_obj.validate_address_multiple_keys(
                address_line_1=address_line_1 or "",
                address_line_2=address_line_2 or ""
            )

        if latitude != 0.0 or longitude != 0.0:
            valid_obj.validate_float_multiple_keys(
                latitude=latitude,
                longitude=longitude
            )

        # ================= REFERRAL CHECK =================
        if referral_code:
            if not Franchise.objects.filter(referral_id=referral_code).exists():
                return Response({'success': '0', 'message': 'Invalid referral code'}, status=status.HTTP_200_OK)

        # ================= MOBILE EMAIL CHECK =================
        if not util_obj.is_mobile_email_available(mobile, email):
            return Response({'success': '0', 'message': 'Mobile number or Email already registered.'}, status=status.HTTP_200_OK)

        # ================= IMAGE VALIDATION =================
        images = {
            "aadhaar_front_image": aadhaar_front_image,
            "aadhaar_back_image": aadhaar_back_image,
            "pan_front_image": pan_front_image
        }

        # Enforce validation only if files are uploaded or required fields are provided
        if aadhaar_number:
            if not aadhaar_front_image or not aadhaar_back_image:
                return Response({'success': '0', 'message': 'Upload of aadhaar front and back images is mandatory when Aadhaar number is provided.'}, status=status.HTTP_200_OK)
        if pan_number:
            if not pan_front_image:
                return Response({'success': '0', 'message': 'Upload of pan front image is mandatory when PAN number is provided.'}, status=status.HTTP_200_OK)

        for key, img in images.items():
            if img:
                errors = valid_obj.validate_image(img, imageType_lst, 'NA', 'NA')
                if errors:
                    return Response({'success': '0', 'message': ', '.join(errors)}, status=status.HTTP_200_OK)

        # ================= PREPARE DATA =================
        unique_id = random_obj.generateUID()
        address_unique_id = random_obj.generateUID()

        directory = f'customer-documents/{unique_id}/'
        upload_dir = os.path.join(settings.MEDIA_ROOT, directory)

        aadhaar_front_name = f'aadhaar_front_{random.randint(100000,999999)}.jpg'
        aadhaar_back_name = f'aadhaar_back_{random.randint(100000,999999)}.jpg'
        pan_front_name = f'pan_front_{random.randint(100000,999999)}.jpg'

        aadhaar_front_path = directory + aadhaar_front_name if aadhaar_front_image else ""
        aadhaar_back_path = directory + aadhaar_back_name if aadhaar_back_image else ""
        pan_front_path = directory + pan_front_name if pan_front_image else ""

        salt, password = encrypt_obj.runEncryprion(password_text)

        logged_user = request.user

        # ================= DATABASE TRANSACTION =================
        with transaction.atomic():

            customer = Customer.objects.create(
                date=current_date,
                unique_id=unique_id,
                name=name,
                aadhaar_number=aadhaar_number,
                aadhaar_front_image=aadhaar_front_path,
                aadhaar_back_image=aadhaar_back_path,
                pan_number=pan_number,
                pan_front_image=pan_front_path,
                mobile=mobile,
                email=email,
                password=password,
                password_text=password_text,
                salt=salt,
                referral_code=referral_code or "",
                token_logged_user=logged_user,
                latitude=latitude,
                longitude=longitude,
                location=bytes(location, 'utf-8') if location else b''
            )

            # Create address only if at least pincode or address_line is provided
            if pincode or postoffice or state or city or address_line_1:
                CustomerAddress.objects.create(
                    date=current_date,
                    unique_id=address_unique_id,
                    name=name,
                    mobile=mobile,
                    pincode=pincode or "",
                    postoffice=postoffice or "",
                    state=state or "",
                    city=city or "",
                    district=district or "",
                    region=region or "",
                    address_line_1=address_line_1 or "",
                    address_line_2=address_line_2 or "",
                    token_logged_user=logged_user,
                    customer=customer
                )

        # ================= SAVE FILES =================
        files = []
        if aadhaar_front_image:
            files.append((aadhaar_front_image, aadhaar_front_name))
        if aadhaar_back_image:
            files.append((aadhaar_back_image, aadhaar_back_name))
        if pan_front_image:
            files.append((pan_front_image, pan_front_name))

        if files:
            util_obj.create_media_folder(directory)
            for file, filename in files:
                file_path = os.path.join(upload_dir, filename)
                with default_storage.open(file_path, 'wb+') as destination:
                    for chunk in file.chunks():
                        destination.write(chunk)
        return Response({'success': '1', 'message': 'Registration done successfully'}, status=status.HTTP_200_OK)
    except ValidationError as e:
        return Response({'success': '0', 'message': str(e)}, status=status.HTTP_200_OK)
    except IntegrityError:
        return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': '0', 'message': 'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def customerLogin(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            password_text = request.POST.get('password','')
            unique_application_id = request.POST.get('unique_application_id','')
            device_details = request.POST.get('device_details','')
            latitude = float(request.POST.get('latitude') or 0)
            longitude = float(request.POST.get('longitude') or 0)
            location = request.POST.get('location','')
            
            if field == "" and mobile != "" and password_text != "" and unique_application_id != "" and device_details != "" and location != "" and latitude != 0 and longitude != 0:
                valid_obj.validate_mobile_number(mobile)
                # valid_obj.validate_password(password_text)
                valid_obj.validate_float_multiple_keys(latitude = latitude, longitude = longitude)
                
                flag = 0
                logged_user = request.user

                login_success = Customer.objects.filter(mobile=mobile)
                if not login_success:
                    return Response({'success':'0','message':'Username or password is incorrect'}, status=status.HTTP_200_OK)
                else:
                    login_id=login_success[0].unique_id
                    db_pass=login_success[0].password
                    db_salt=login_success[0].salt
                    # print(db_salt)
                    # print(db_pass)
                    password = encrypt_obj.encryption(db_salt,password_text)
                    # print(password)
                    
                    if password == db_pass:
                        if login_success[0].access=="Granted":
                            with transaction.atomic():
                                if login_success[0].unique_application_id == '':
                                    affected_rows = login_success.update(
                                    app_id_date = current_date,
                                    unique_application_id = unique_application_id,
                                    device_details = bytes(device_details,'utf-8'))

                                    if affected_rows>0:
                                        flag = 1
                                    else:
                                        return Response({'success':'0','message':'1 Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
                                elif login_success[0].unique_application_id != '':
                                    if login_success[0].unique_application_id == unique_application_id:
                                        flag = 1
                                    else:
                                        return Response({'success':'0','message':'Multiple device login not allowed.'}, status=status.HTTP_200_OK) 

                                if flag == 1:
                                    insertData = CustomerLoginReport.objects.create(
                                        username = mobile,
                                        login_date_time = current_date,
                                        latitude = latitude,
                                        longitude = longitude,
                                        location = bytes(location,'utf-8'),
                                        customer = Customer.objects.get(unique_id=login_id),
                                        token_logged_user = logged_user,
                                    )
                                    if insertData:
                                        return Response({'success':'1','user_unique_id':login_id, 'mobile_number':mobile, 'name': login_success[0].name, 'email': login_success[0].email, 'access':login_success[0].access }, status=status.HTTP_200_OK)
                                    else:
                                        return Response({'success':'0','message':'2 Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':'0','message':'You are blocked by the administation. Kindly contact company manager for more details!'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'Username or password is incorrect'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            # util_obj.rollbacktable(['customer','customer_login_report'])
            # error_message = str(e)
            # if "Duplicate entry" in error_message:
            #     # Extract column name
            #     column_name = error_message.split("for key '")[1].split("'")[0]
            #     return Response({'success':'0','message':f"The value already exists for {column_name.capitalize()}!"}, status=status.HTTP_200_OK)
            # else:
            #     return Response({'success':'0','message':error_message}, status=status.HTTP_200_OK)
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'3 Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def checkCustomerAppAccess(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                login_success = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id)
                if login_success:
                    if login_success[0].access=="Granted":
                        return Response({'success':'1', 'access':login_success[0].access}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'You are blocked by the administation. Kindly contact company manager for more details!'}, status=status.HTTP_200_OK)
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
def checkUniqueAppId(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            unique_application_id = request.POST.get('unique_application_id','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and unique_application_id != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                login_success = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id)
                if login_success:
                    if login_success[0].unique_application_id == unique_application_id:
                        return Response({'success':'1', 'message':'Device id matched'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'Device id not matched'}, status=status.HTTP_200_OK)
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
def storeFCMId(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            fcm_registered_id = request.POST.get('fcm_registered_id','')
            # user_unique_id = request.POST.get('user_unique_id','')
            
            # if field == "" and mobile != "" and fcm_registered_id != "" and user_unique_id != "":
            if field == "" and mobile != "" and fcm_registered_id != "":
                valid_obj.validate_mobile_number(mobile)
                # valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                # login_success = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id)
                login_success = Customer.objects.filter(mobile = mobile)
                if login_success:
                    affected_rows = login_success.update(
                    fcm_date = current_date,
                    fcm_registered_id = fcm_registered_id)

                    if affected_rows>0:
                        return Response({'success':'1','message':'FCM Id updated successfully.'}, status=status.HTTP_200_OK) 
                    else:
                        return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
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
def storeUniqueAppId(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            unique_application_id = request.POST.get('unique_application_id','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and unique_application_id != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                login_success = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id)
                if login_success:
                    affected_rows = login_success.update(
                    app_id_date = current_date,
                    unique_application_id = unique_application_id,)

                    if affected_rows>0:
                        return Response({'success':'1','message':'Application Id updated successfully.'}, status=status.HTTP_200_OK) 
                    else:
                        return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK) 
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
def profile(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(user_id = user_unique_id)

                data = []
                login_success = Customer.objects.filter(mobile = mobile, unique_id = user_unique_id)[0]
                if login_success:
                    data = custObj.getCustomer(login_success)
                    return Response(data, status=status.HTTP_200_OK)
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
def forgotPassword(request):
    if request.method == 'POST':
        try:
            field = request.POST['field']
            mobile = request.POST.get('mobile','')
            
            if field == "" and mobile != "":
                valid_obj.validate_mobile_number(mobile)

                login_success = Customer.objects.filter(mobile=mobile, access='Granted').first()
                if not login_success:
                    return Response({'success':'0','message':'This user is not registered.'}, status=status.HTTP_200_OK)
                else:
                    # Generate Unique ID
                    unique_id = str(uuid.uuid4())
                    valid_till = timezone.now() + timedelta(hours=2)
                    # valid_till = timezone.now() + timedelta(minutes=60)

                    logged_user = login_success.mobile
                    email = login_success.email
                    page_name = 'set-customer-password'

                    PasswordResetRequest.objects.filter(email=email, password_changed="No").update(link_status="Expired")

                    with transaction.atomic():
                        insertData = PasswordResetRequest.objects.create(
                            email = email,
                            request_date_time = current_date,
                            valid_till = valid_till,
                            unique_id = unique_id,
                            customer = login_success,
                            token_logged_user = logged_user
                        )
                        if insertData:
                            mail_obj.passwordReset(login_success.name, email, login_success.mobile, unique_id, page_name, domainURL)

                            return Response({'success':'1','message':'Password reset request sent to your registered mail id.'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def addCustomerAddress(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            name = request.POST.get('name','')
            add_mobile = request.POST.get('add_mobile','') 
            pincode = request.POST.get('pincode','')
            postoffice = request.POST.get('postoffice','')
            state = request.POST.get('state','')
            city = request.POST.get('city','')
            district = request.POST.get('district','')
            region = request.POST.get('region','')
            address_line_1 = request.POST.get('address_line_1','')
            address_line_2 = request.POST.get('address_line_2','')
            
            if field == "" and mobile != "" and user_unique_id != "" and name != "" and add_mobile != "" and pincode != "" and postoffice != "" and state != "" and city != "" and region != "" and address_line_1 != "" and address_line_2 != "":
                valid_obj.validate_alpha_multiple_keys(name = name)
                valid_obj.validate_address_component_multiple_keys(postoffice = postoffice, state = state, city = city, region = region, district = district)
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_mobile_number(add_mobile)
                valid_obj.validate_pincode(pincode)
                valid_obj.validate_address_multiple_keys(address_line_1 = address_line_1, address_line_2 = address_line_2)
                
                unique_id = random_obj.generateUID()
                logged_user = request.user

                with transaction.atomic():
                    insertAddressData = CustomerAddress.objects.create(
                        date = current_date,
                        unique_id = unique_id,
                        name = name,
                        mobile = add_mobile,
                        pincode = pincode,
                        postoffice = postoffice,
                        state = state,
                        city = city,
                        district = district,
                        region = region,
                        address_line_1 = address_line_1,
                        address_line_2 = address_line_2,
                        token_logged_user = logged_user,
                        customer = Customer.objects.get(unique_id=user_unique_id),
                    )
                    if insertAddressData:
                        return Response({'success':'1','message':'Address added successfully'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def updateCustomerAddress(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            unique_id = request.POST.get('unique_id','')
            name = request.POST.get('name','')
            add_mobile = request.POST.get('add_mobile','')
            pincode = request.POST.get('pincode','')
            postoffice = request.POST.get('postoffice','')
            state = request.POST.get('state','')
            city = request.POST.get('city','')
            district = request.POST.get('district','')
            region = request.POST.get('region','')
            address_line_1 = request.POST.get('address_line_1','')
            address_line_2 = request.POST.get('address_line_2','')
            
            if field == "" and mobile != "" and user_unique_id != "" and unique_id != "" and name != "" and add_mobile != "" and pincode != "" and postoffice != "" and state != "" and city != "" and region != "" and address_line_1 != "" and address_line_2 != "":
                valid_obj.validate_alpha_multiple_keys(name = name)
                valid_obj.validate_address_component_multiple_keys(postoffice = postoffice, state = state, city = city, region = region, district = district)
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_mobile_number(add_mobile)
                valid_obj.validate_pincode(pincode)
                valid_obj.validate_address_multiple_keys(address_line_1 = address_line_1, address_line_2 = address_line_2)
                
                with transaction.atomic():
                    obj = CustomerAddress.objects.filter(unique_id = unique_id, customer__unique_id = user_unique_id)
                    if obj:
                        affected_rows = obj.update(
                        name = name,
                        mobile = add_mobile,
                        pincode = pincode,
                        postoffice = postoffice,
                        state = state,
                        city = city,
                        district = district,
                        region = region,
                        address_line_1 = address_line_1,
                        address_line_2 = address_line_2)

                        if affected_rows>0:
                            return Response({'success':'1','message':'Address updated successfully'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def customerAddressList(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                data = custObj.getCustomerAddressList(user_unique_id)
                if len(data) > 0:
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)   