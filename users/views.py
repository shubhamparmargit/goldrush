from django.shortcuts import render
from utility.views import Utility, RandomIdGenerate, Encryption, Validation, current_date, ROLE_FRANCHISE_MAP, urlPrefix
from django.http.response import JsonResponse
from rest_framework import status
import re, os, random
from django.db import transaction, IntegrityError
from users.models import Franchise, FranchiseBankDetails, FranchiseDocuments
from authentication.models import Login, User_Role
from customer.models import Customer, ReferralHistory
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
    def franchise_module(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/franchise-module.html')
        else:
            return util_obj.goToLogin(request)
        
    def franchise_list(self,request):
        if util_obj.checkSession(request) == False:
            context = {
                "ROLE_FRANCHISE_MAP": ROLE_FRANCHISE_MAP.items()
            }
            return render(request,'portal/franchise-list.html',context)
        else:
            return util_obj.goToLogin(request)

company_support_id = 'GD01' 
class TradingUser:
    def saveTradingUser(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    errors = {}

                    rules = {
                        "franchise_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                        "holder_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                        "email": (r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", "Please enter a valid email address."),
                        "mobile": (r"^[0-9]{10}$", "Please enter a valid 10-digit mobile number."),
                        "aadhaar_number": (r"^[0-9]{12}$", "Aadhar card should be 12 digits long."),
                        "pan_number": (r"^([A-Z]){5}([0-9]){4}([A-Z]){1}$", "Please enter a valid PAN card number."),
                        "gst_number": (r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$", "Please enter a valid GST number"),
                        "agent_id": (r"^[A-Za-z0-9\-]+$", "Invalid agent id" ),
                        "bank_name": (r"^[A-Za-z.&\s]+$", "Please input alphabet characters only."),
                        "account_holder_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                        "account_number": (r"^[0-9]+$", "Please enter a valid account number."),
                        "ifsc_code": (r"^[A-Za-z]{4}0[A-Z0-9a-z]{6}$", "Please enter valid IFSC code"),
                        "branch_name": (r"^[A-Za-z.\s]+$", "Please input alphabet characters only."),
                        "commission_slab": (r"^[0-9]+$", "Please enter a valid commission slab."),
                        "commission_percentage": (r"^[0-9]+$", "Please enter a valid commission percentage."),
                    }

                    required_fields = [
                        "franchise_type",
                        "franchise_name", "holder_name",
                        "mobile", "email",
                        "aadhaar_number", "pan_number",
                        "bank_name", "account_holder_name",
                        "account_number", "ifsc_code",
                        "commission_slab", "commission_percentage"
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
                    allowed_ext = (".jpg", ".jpeg", ".png", ".pdf")
                    max_file_size = 5 * 1024 * 1024  # 5MB
                    allowed_mime = ["image/jpeg","image/png","application/pdf"]
                    required_files = ["aadhaar_doc", "pan_doc", "agreement_doc"]
                    # optional_files = ["cancelled_cheque", "passbook", "bank_statement"]
                    optional_files = ["cancelled_cheque", "passbook"]

                    for file_field in required_files:
                        f = request.FILES.get(file_field)
                        if not f:
                            errors[file_field] = "This document is required"
                        elif not f.name.lower().endswith(allowed_ext):
                            errors[file_field] = "Only JPG, PNG and PDF files are allowed"
                        elif f.content_type not in allowed_mime:
                            errors[field_name] = "Invalid file type"
                        elif f.size > max_file_size:
                            errors[field_name] = "File size should not exceed 5MB"

                    # 🟡 OPTIONAL FILES CHECK (only if uploaded)
                    for file_field in optional_files:
                        f = request.FILES.get(file_field)
                        if f:
                            if not f.name.lower().endswith(allowed_ext):
                                errors[file_field] = "Only JPG, PNG and PDF files are allowed"
                            elif f.content_type not in allowed_mime:
                                errors[field_name] = "Invalid file type"
                            elif f.size > max_file_size:
                                errors[field_name] = "File size should not exceed 5MB"

                    # ================= FINAL RESPONSE =================
                    if errors:
                        return JsonResponse({'success':'2','message':'Validation errors',"errors": errors}, status=status.HTTP_200_OK)
                    
                    # ================= CHECK MOBILE EMAIL =================
                    mobile = request.POST.get("mobile")
                    email = request.POST.get("email")
                    if not util_obj.is_mobile_email_available(mobile, email):
                        return JsonResponse({"success": '0', "message": "Mobile number or Email already registered."}, status=status.HTTP_200_OK)
                    
                    # ================= FETCH SESSION =================
                    login_id = request.session['login_id']
                    username = request.session['logged']
                    role = request.session['role']

                    # ================= GET MODEL AND PARENT =================
                    if role == 1:
                        # 🔵 SUPER ADMIN (Manual selection from form)
                        franchise_model = request.POST.get("franchise_model")

                        parent_unique_id = request.POST.get("parent_franchise")
                        parent_id = None

                        # ❗ Validation
                        if not franchise_model:
                            return JsonResponse({
                                'success': 0,
                                'message': 'Franchise type is required'
                            })

                        # SMRA → root
                        if franchise_model != 'SMRA':
                            if not parent_unique_id:
                                return JsonResponse({
                                    'success': 0,
                                    'message': 'Parent franchise is required'
                                })

                            try:
                                parent_franchise = Franchise.objects.get(unique_id=parent_unique_id)
                                parent_id = parent_franchise.id
                            except Franchise.DoesNotExist:
                                return JsonResponse({
                                    'success': 0,
                                    'message': 'Selected parent franchise does not exist'
                                })

                    else:
                        # 🔵 NON–SUPER ADMIN (Auto logic – EXISTING CODE)
                        franchise_model, parent_id = self.get_auto_franchise_data(role, login_id)

                    # ================= FETCH FORM DATA =================
                    # franchise_model = request.POST.get("franchise_model")
                    franchise_type = request.POST.get("franchise_type")
                    franchise_name = request.POST.get("franchise_name")
                    holder_name = request.POST.get("holder_name")
                    address = request.POST.get("address")

                    aadhaar_number = request.POST.get("aadhaar_number")
                    pan_number = request.POST.get("pan_number")
                    gst_number = request.POST.get("gst_number")
                    agent_id = request.POST.get("agent_id")

                    bank_name = request.POST.get("bank_name")
                    account_holder_name = request.POST.get("account_holder_name")
                    account_number = request.POST.get("account_number")
                    ifsc_code = request.POST.get("ifsc_code")
                    branch_name = request.POST.get("branch_name")

                    commission_slab = request.POST.get("commission_slab")
                    commission_percentage = request.POST.get("commission_percentage")

                    access = "Granted" if request.POST.get("access") else "Blocked"

                    # ================= GENERATE UNIQUE IDS =================
                    unique_id = random_obj.generateUID()
                    bank_unique_id = random_obj.generateUID()

                    # ================= GENERATE REFERRAL DATA =================
                    referral_prefix = franchise_model
                    referral_id, referral_sequence = self.generate_referral_id(referral_prefix)

                    # ================= GENERATE PASSWORD DATA =================
                    password_text = random_obj.generate_short_uuid(10)
                    salt, password = encrypt_obj.runEncryprion(password_text)

                    # ================= GET ROLE =================
                    role = User_Role.get_by_franchise_model(franchise_model)

                    with transaction.atomic():
                        # ================= CREATE FRANCHISE =================
                        franchise = Franchise.objects.create(
                            date=current_date,
                            unique_id=unique_id,
                            parent_id=parent_id,
                            franchise_model=franchise_model,
                            company_support_id=company_support_id,
                            referral_id=referral_id,
                            referral_prefix=referral_prefix,
                            referral_sequence=referral_sequence,
                            franchise_type=franchise_type,
                            franchise_name=franchise_name,
                            holder_name=holder_name,
                            aadhaar_number=aadhaar_number,
                            pan_number=pan_number,
                            gst_number=gst_number,
                            agent_id=agent_id,
                            mobile=mobile,
                            email=email,
                            address=address,
                            commission_slab=commission_slab,
                            commission_percentage=commission_percentage,
                            access=access,
                            created_by=login_id
                        )

                        # ================= CREATE LOGIN =================
                        login = Login.objects.create(
                            date=current_date,
                            name=holder_name,
                            mobile_number=mobile,
                            email=email,
                            password=password,
                            salt=salt,
                            password_text=password_text,
                            access=access,
                            role=role,
                            added_by=username,
                            table_name="franchise",
                            table_id=unique_id
                        )

                        # ================= BANK DETAILS =================
                        FranchiseBankDetails.objects.create(
                            franchise=franchise,
                            unique_id=bank_unique_id,
                            date=current_date,
                            bank_name=bank_name,
                            account_holder_name=account_holder_name,
                            account_number=account_number,
                            ifsc_code=ifsc_code,
                            branch_name=branch_name
                        )

                        # ================= DOCUMENTS =================
                        base_dir = os.path.join(settings.MEDIA_ROOT, f"franchise-documents/{unique_id}/")
                        os.makedirs(base_dir, exist_ok=True)

                        documents = {
                            "aadhaar_doc": ("AADHAAR", "aadhaar"),
                            "pan_doc": ("PAN", "pan"),
                            "agreement_doc": ("AGREEMENT", "agreement"),

                            "cancelled_cheque": ("BANK_CHEQUE", "cancelled_cheque"),
                            "passbook": ("BANK_PASSBOOK", "passbook"),
                            # "bank_statement": ("BANK_STATEMENT", "bank_statement"),
                        }

                        for field_name, (doc_type, file_prefix) in documents.items():
                            file_obj = request.FILES.get(field_name)
                            if not file_obj:
                                continue

                            file_name = util_obj.save_document(file_obj, base_dir, file_prefix)

                            FranchiseDocuments.objects.create(
                                franchise=franchise,
                                unique_id=random_obj.generateUID(),
                                date=current_date,
                                doc_type=doc_type,
                                file_path=f"franchise-documents/{unique_id}/{file_name}"
                            )

                        util_obj.activity_log(login_id, username, "Franchise", f"Franchise Created => {unique_id}")

                        return JsonResponse({
                            "success": 1,
                            "message": "Franchise created successfully"
                        })
                # except IntegrityError:
                #     return JsonResponse({
                #         "success": 0,
                #         "message": "Mobile or Email already exists"
                #     })
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
        
    def generate_referral_id(self,prefix):
        with transaction.atomic():
            # last sequence fetch (prefix wise)
            last_seq = (
                Franchise.objects
                .select_for_update()
                .filter(referral_prefix=prefix)
                .aggregate(max_seq=Max('referral_sequence'))
                .get('max_seq')
            )

            next_seq = (last_seq or 0) + 1

            referral_id = f"{prefix}{str(next_seq).zfill(3)}"

            return referral_id, next_seq
        
    def get_auto_franchise_data(self,role,login_id):
        if role not in ROLE_FRANCHISE_MAP:
            raise Exception("Invalid role")

        # 🔹 New franchise model
        franchise_model = ROLE_FRANCHISE_MAP[role]

        parent_id = None

        # 🔹 Super Admin → no parent
        if role != 1:
            login = Login.objects.get(id=login_id)
            parent_franchise = Franchise.objects.get(unique_id=login.table_id)
            parent_id = parent_franchise.id

        return franchise_model, parent_id

    def getUser(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('trading_user') is not None:
                        unique_id = request.POST.get("unique_id", "").strip()

                        if not unique_id:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                            
                        digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                        if digit_validate != 1:
                            return util_obj.printErrorResponse_200(digit_validate)

                        franchise = Franchise.objects.filter(unique_id=unique_id).select_related('parent').first()

                        if not franchise:
                            return util_obj.printErrorResponse_200('Data not found!')
                        
                        parent_name = ''
                        parent_referral_id = ''

                        if franchise and franchise.parent:
                            parent_name = franchise.parent.franchise_name
                            parent_referral_id = franchise.parent.referral_id
                        
                        register_date_time = timezone.localtime(franchise.date).strftime('%d-%m-%Y @ %I:%M %p')
                        # bankList = self.getFranchiseDetails(franchise.unique_id, include_bank=True)
                        # docList = self.getFranchiseDetails(franchise.unique_id, include_docs=True)
                        franchiseDetails = self.getFranchiseDetails(franchise.unique_id,include_bank=True,include_docs=True)
                                    
                        data = {'success':'1','register_date_time':register_date_time, 'unique_id':franchise.unique_id, 'franchise_name':franchise.franchise_name, 'aadhaar_number':franchise.aadhaar_number, 'pan_number':franchise.pan_number, 'mobile':franchise.mobile, 'email':franchise.email, 'referral_id':franchise.referral_id, 'franchise_model':franchise.franchise_model, 'holder_name':franchise.holder_name, 'access':franchise.access, 'address':franchise.address, 'company_support_id':franchise.company_support_id, 'agent_id':franchise.agent_id, 'gst_number':franchise.gst_number, 'commission_slab':franchise.commission_slab, 'commission_percentage':franchise.commission_percentage, 'parent_name': parent_name,'parent_referral_id': parent_referral_id, 'franchiseDetails':franchiseDetails}
                                
                        return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
                    
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                
                except Exception as e:
                    # print("getUser error:", e)
                    
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            
            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        
        return util_obj.goToLogin(request)
    
    def getFranchiseDetails(self,franchise_unique_id,include_bank=False,include_docs=False):
        result = {}

        if include_bank:
            bank_qs = FranchiseBankDetails.objects.filter(
                franchise__unique_id=franchise_unique_id
            )

            bank_list = []
            sr_no = 1
            for row in bank_qs:
                bank_list.append({
                    'sr_no': sr_no,
                    'unique_id': row.unique_id,
                    'bank_name': row.bank_name,
                    'account_holder_name': row.account_holder_name,
                    'account_number': row.account_number,
                    'ifsc_code': row.ifsc_code,
                    'branch_name': row.branch_name,
                    'date': timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
                })
                sr_no += 1

            result["bank_details"] = bank_list

        if include_docs:
            doc_qs = FranchiseDocuments.objects.filter(
                franchise__unique_id=franchise_unique_id
            )

            doc_list = []
            sr_no = 1
            for row in doc_qs:
                doc_list.append({
                    'sr_no': sr_no,
                    'unique_id': row.unique_id,
                    'doc_type': row.doc_type,
                    'file_path': urlPrefix+row.file_path,
                    'date': timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
                })
                sr_no += 1

            result["documents"] = doc_list

        return result
    
    def getParentFranchises(self,request):
        if request.method == 'POST':
            model = request.POST.get('franchise_model')
            parent_map = {'MRA':'SMRA','RA':'MRA','User':'RA'}
            parent_type = parent_map.get(model)
            if parent_type:
                parents = Franchise.objects.filter(franchise_model=parent_type)
                parent_list = [
                    {'unique_id': f.unique_id, 'franchise_name': f.franchise_name, 'referral_id': f.referral_id} 
                    for f in parents
                ]
                return JsonResponse({'parents': parent_list})
            return JsonResponse({'parents': []})
        
    def build_tree(self,franchise):
        return {
            "id": franchise.unique_id,
            "name": franchise.holder_name,
            "model": franchise.franchise_model,
            "mobile": franchise.mobile,
            "email": franchise.email,
            "status": franchise.status,
            "children": [
                self.build_tree(child)
                for child in franchise.children.all()
            ]
        }

    def franchise_hierarchy(self,request):
        franchise_id = request.POST.get('franchise_id')

        try:
            root = Franchise.objects.get(unique_id=franchise_id)
        except Franchise.DoesNotExist:
            return JsonResponse({"status": False, "msg": "Invalid franchise"})

        data = self.build_tree(root)

        return JsonResponse({
            "status": True,
            "data": data
        })

    def update_franchise_status(self,request):
        if request.method != 'POST':
            return JsonResponse({
                'success': 0,
                'message': 'Invalid request method'
            })

        franchise_uid = request.POST.get('franchise_id')
        franchise_status = request.POST.get('status')

        # print(franchise_status)

        # ✅ BASIC VALIDATION
        if not franchise_uid:
            return JsonResponse({
                'success': 0,
                'message': 'Invalid franchise ID'
            })

        if franchise_status not in ['Approved', 'Rejected']:
            return JsonResponse({
                'success': 0,
                'message': 'Invalid status value'
            })

        # try:
        with transaction.atomic():
            franchise = Franchise.objects.select_for_update().get(
                unique_id=franchise_uid
            )

            # ❗ SAME STATUS CHECK (No changes)
            if franchise.status == franchise_status:
                return JsonResponse({
                    'success': 0,
                    'message': 'No changes detected'
                })

            # 🔄 UPDATE
            franchise.status = franchise_status
            franchise.status_date = current_date
            franchise.save(update_fields=['status', 'status_date'])

            # 🔔 OPTIONAL: EXTRA ACTION ON ACCEPT
            if franchise_status == 'Approved':
                login = Login.objects.filter(
                    table_id=franchise.unique_id
                ).first()

                if login:
                    mail_obj.welcomeMessage(
                        franchise.holder_name,
                        franchise.email,
                        franchise.mobile,
                        login.password_text
                    )

            return JsonResponse({
                'success': 1,
                'message': f'Franchise {franchise_status} successfully!'
            })

        # except Franchise.DoesNotExist:
        #     return JsonResponse({
        #         'success': 0,
        #         'message': 'Franchise not found'
        #     })

        # except Exception:
        #     return JsonResponse({
        #         'success': 0,
        #         'message': 'Something went wrong. Please try again later.'
        #     })

    def getAllAgents(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    agent_list=Franchise.objects.filter(access__exact = 'Granted', franchise_model__exact = 'RA')
                    data=[]
                    if len(agent_list)>0:
                        for row in agent_list:
                            data.append({'referral_id':row.referral_id, 'holder_name':row.holder_name})
                    return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
    def transferAgent(self,request):
        if request.method != 'POST':
            return JsonResponse({'success': 0,'message': 'Invalid request method'})

        customer_id = request.POST.get('customer_id')
        referral_agent = request.POST.get('referral_agent')
        reason_for_transfer = request.POST.get('reason_for_transfer')

        # ✅ BASIC VALIDATION
        if not customer_id:
            return JsonResponse({'success': 0,'message': 'Invalid customer ID'})
        
        if not referral_agent:
            return JsonResponse({'success': 0,'message': 'Referral agent is required'})
        
        if not Franchise.objects.filter(referral_id=referral_agent).exists():
            return JsonResponse({'success': 0,'message': 'Invalid referral agent'})
        
        transfer_by = request.session.get('logged', 'system')

        try:
            with transaction.atomic():
                customer = Customer.objects.select_for_update().get(unique_id=customer_id)
                old_referral_code = customer.referral_code

                if old_referral_code == referral_agent:
                    return JsonResponse({'success': 0,'message': 'Customer already assigned to this agent'})

                customer.referral_code = referral_agent
                customer.save(update_fields=['referral_code'])

                ReferralHistory.objects.create(
                    unique_id = random_obj.generateUID(),
                    customer=customer,
                    old_referral_code=old_referral_code,
                    new_referral_code=referral_agent,
                    transfer_by=transfer_by,
                    transfer_date = current_date,
                    reason_for_transfer=reason_for_transfer
                )

                return JsonResponse({'success': 1,'message': 'Referral Agent Changed Successfully!'})
        except Customer.DoesNotExist:
            return JsonResponse({'success': 0, 'message': 'Customer not found'})
        except Exception as e:
            print("Transfer Error:", str(e))
            return JsonResponse({'success': 0,'message': 'Something went wrong. Please try again later.'})