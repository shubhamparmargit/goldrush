from decimal import Decimal, InvalidOperation
import hashlib, os, re, uuid, string, math, secrets, re, random, json
from django.shortcuts import render
from django.http.response import JsonResponse
from rest_framework import status
from datetime import datetime
from django.db import connection, transaction
from django.apps import apps
from authentication.models import User_Activity_Log, Login
from product.models import MetalPurityPrice, Unit, Category, Product, Stock, StockMovement
from customer.models import Customer, CustomerLoginReport, CustomerAddress, ReferralHistory
from customer_trading.models import CustomerTradingAccount
from customer_order.models import Cart, Order
from portal_misc.models import ImageSlider
from website.models import ContactMessage
from django.db.models import Count, Sum
from django.db.models import Q
from django.core.files.images import get_image_dimensions
from django.conf import settings
from django.core.exceptions import ValidationError
from num2words import num2words
from users.models import Franchise
from customer_wallet.models import MembershipMaster, CustomerWallet, CustomerDemoWallet, WalletRechargeHistory, WithdrawalRequest
from customer_transaction.models import CustomerTransaction, CustomerDemoTransaction
from decimal import Decimal, ROUND_HALF_UP
from django.utils import timezone
from datetime import timedelta
from django.db.models import OuterRef, Subquery, Exists
from openpyxl import Workbook
from django.http import HttpResponse

current_date = datetime.now()
imageType_lst = ['.jpg','.jpeg','.png']
urlPrefix = settings.DOMAIN_NAME+'media/'
domainURL = settings.DOMAIN_NAME
domainURLPortal = settings.DOMAIN_NAME_PORTAL

ROLE_FRANCHISE_MAP = {
    1: "SMRA",   # Super Admin creates SMRA
    2: "MRA",    # SMRA creates MRA
    3: "RA",    # MRA creates RA
}

TABLE_MODEL_MAP = {
    'metal_purity_price': ('product', 'MetalPurityPrice'),
    'unit': ('product', 'Unit'),
    'category': ('product', 'Category'),
    'product': ('product', 'Product'),
    'image_slider': ('portal_misc', 'ImageSlider'),
    'customer': ('customer', 'Customer'),
    'trading_user': ('users', 'Franchise'),
    'portal_user' : ('authentication', 'Login')
}

EXPORT_COLUMNS = {
    "registration_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("State", "state"),
        ("Creation Time","date"),
        ("Last Login Date", "last_login"),
        ("Last Login Latitude", "latitude"),
        ("Last Login Longitude", "longitude")
    ],
    "wallet_recharge_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Registered On", "date"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Transaction Amount", "amount"),
        ("Transaction Date", "transaction_date"),
        ("Membership", "membership"),
        ("Razorpay Order ID", "razorpay_order_id"),
        ("Razorpay Payment ID", "razorpay_payment_id"),
    ],
    "first_recharge_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Registered On", "date"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Transaction Amount", "amount"),
        ("Transaction Date", "transaction_date"),
        ("Membership", "membership"),
        ("Razorpay Order ID", "razorpay_order_id"),
        ("Razorpay Payment ID", "razorpay_payment_id"),
    ],
    "transaction_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Metal", "metal_type"),
        ("Quantity", "quantity"),
        ("Invested Amount", "invested_amount"),
        ("Buy Rate", "buy_price"),
        ("Buy Date", "buy_date"),
        ("Sell Rate", "sell_price"),
        ("Sell Date", "sell_date"),
        ("Order Type", "order_type"),
        ("Profit/Loss", "profit_loss"),
        ("PNL Amount", "pnl_amount"),
    ],
    "trading_user": [
        ("Sr. No.", "sr_no"),
        ("Registered On", "date"),
        ("Referral Id", "referral_id"),
        ("Franchise Name", "franchise_name"),
        ("Holder Name", "holder_name"),
        ("Mobile No.", "mobile"),
        ("Email", "email"),
        ("Status", "status"),
    ],
    "customer_report": [
        ("Sr. No.", "sr_no"),
        ("Creation Date & Time", "date"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Email", "email"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Aadhaar Number", "aadhaar_number"),
        ("PAN Number", "pan_number"),
        ("Addresses", "addresses"),
        ("Ecomm Access", "access"),
        ("Trading Option", "trading"),
        ("Trading Status", "trading_status"),
        ("Trading Account Type", "account_type"),
        ("Bank Name", "bank_name"),
        ("Account Holder Name", "account_holder_name"),
        ("Account Number", "account_number"),
        ("IFSC Code", "ifsc_code"),
        ("Branch Name", "branch_name"),
        ("Documents", "documents"),
        ("Last Login Date", "last_login"),
        ("Last Login Latitude", "latitude"),
        ("Last Login Longitude", "longitude"),
    ],
    "order_report": [
        ("Sr. No.", "sr_no"),
        ("Order Date", "order_date"),
        ("Order Number", "order_number"),
        ("Order ID", "order_id"),
        ("Customer Name", "customer_name"),
        ("Mobile", "mobile"),
        ("Email", "email"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Product Detail ID", "product_detail_id"),
        ("Product Name", "product_name"),
        ("Category", "category"),
        ("Quantity", "quantity"),
        ("Price", "price"),
        ("Total", "total"),
        ("Total Items", "total_items"),
        ("Total Quantity", "total_quantity"),
        ("Sub Total", "sub_total"),
        ("Product Status", "product_status"),
        ("Status History", "status_history"),
        ("Remark", "remark"),
        ("Razorpay Order ID", "razorpay_order_id"),
        ("Razorpay Payment ID", "razorpay_payment_id"),
        ("Payment Status", "payment_status"),
        ("Address Name", "address_name"),
        ("Address Mobile", "address_mobile"),
        ("Pincode", "pincode"),
        ("Post Office", "postoffice"),
        ("State", "state"),
        ("City", "city"),
        ("District", "district"),
        ("Region", "region"),
        ("Address Line 1", "address_line_1"),
        ("Address Line 2", "address_line_2"),
    ],
    "inactive_no_recharge": [
        ("Sr. No.", "sr_no"),
        ("Creation Date & Time","date"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile"),
        ("Email", "email"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Trading", "trading"),
        ("Status","status"),
    ],
    "inactive_customers": [
        ("Sr. No.", "sr_no"),
        ("Creation Date & Time","date"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile"),
        ("Email", "email"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Last Login", "last_login"),
        ("Last Transaction","last_transaction"),
        ("Days Inactive","days_inactive"),
    ],
    "customer_transfer_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Registered On", "date"),
        ("Old Referral Code", "old_referral_code"),
        ("New Referral Code", "new_referral_code"),
        ("Transfer Date", "transfer_date"),
        ("Reason For Transfer", "reason_for_transfer"),
    ],
    "withdrawal_report": [
        ("Sr. No.", "sr_no"),
        ("Full Name", "customer_name"),
        ("Mobile Number", "mobile_number"),
        ("Registered On", "date"),
        ("Referral Code", "referral_code"),
        ("Referral Holder Name", "referral_holder_name"),
        ("Request Amount", "request_amount"),
        ("Request Date", "request_date"),
        ("Service Charge", "service_charge"),
        ("GST (18%)", "gst_amount"),
        ("Total Deduction", "total_deduction"),
        ("Final Amount", "final_amount"),
        ("Status", "status"),
        ("Processed On", "action_date"),
        ("Transaction No", "transaction_number"),
        ("Remark", "remark"),
        ("Account Holder Name", "account_holder_name"),
        ("Account Number", "account_number"),
        ("IFSC Code", "ifsc_code"),
        ("Bank Name", "bank_name"),
    ],  
}

class Pages:
    def javascript_disabled(self,request):
        return render(request, 'portal/middleware/javascript-disabled.html')
    
    def check_role_access(self,request):
        return render(request, 'portal/middleware/unauthorized.html')

class Encryption:
    def encryption(self,salt,user_pass):
        key = hashlib.pbkdf2_hmac(
                'sha256', # The hash digest algorithm for HMAC
                user_pass.encode('utf-8'), # Convert the password to bytes
                # salt, # Provide the salt
                bytes.fromhex(salt),  # Convert salt from hex to bytes
                100000 # It is recommended to use at least 100,000 iterations of SHA-256 
                # dklen=128 # Get a 128 byte key
            )
        # Store them as:
        # new_password=salt + key
        # return new_password
        return key.hex()

    def generate_salt(self):
        """Generate a random 32-byte salt and return it in hex format."""
        return os.urandom(32).hex()

    def runEncryprion(self,passwordText):
        # salt = os.urandom(32)
        # encrypt=Encryption()
        # new_pass=encrypt.encryption(salt,"Gold$Mines@2025#")
        # print("Insert Salt :: ",salt)
        # print("Insert Pass :: ",new_pass)
        salt = self.generate_salt()  # Generate salt in hex format
        new_pass = self.encryption(salt,passwordText)
        return salt, new_pass

class Utility:
    def getIPAddress(self,request):
        # get ip address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ipaddress = x_forwarded_for.split(',')[-1].strip()
        else:
            ipaddress = request.META.get('REMOTE_ADDR')
        return ipaddress
    
    def printErrorResponse_200(self,message):
        return JsonResponse({'success':'0','message':message}, status=status.HTTP_200_OK)
    
    def printSuccessResponse_200(self,message):
        return JsonResponse({'success':'1','message':message}, status=status.HTTP_200_OK)

    def activity_log(self,login_id,login_name,page_name,message):
        try:
            insertData = User_Activity_Log.objects.create(
                date = current_date,
                username = login_name,
                page_name = page_name,
                message = bytes(message,'utf-8'),
                login = Login.objects.get(id=login_id),
            )
            if insertData:
                pass
            else:
                return self.printErrorResponse_200('Something went wrong. Please try again later.')
        except:
            return self.printErrorResponse_200('Something went wrong. Please try again later.') 

    def checkSession(self,request):
        if request.session.get('logged') is None or request.session.get('logged') == '':
            return True
        else:
            return False
        
    def goToLogin(self,request):
        request.session.clear()
        return render(request,'portal/login.html')

    def rollbacktable(self,tables):
        with connection.cursor() as cursor:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
            if isinstance(tables,list):
                for table in tables:
                    cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
            else:
                cursor.execute(f"ALTER TABLE {table} AUTO_INCREMENT = 1;")
            cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")

    def formatPrice(self,price):
        return f"{price:.4f}".rstrip('0').rstrip('.')

    def get_image_path(self,foldername,mediapath):
        return os.path.join(foldername, mediapath)
    
    def create_media_folder(self,path):
        if not os.path.exists(self.get_image_path(path,os.path.join(settings.MEDIA_ROOT,self.get_image_path(path,'')))):
            os.makedirs(self.get_image_path(path,os.path.join(settings.MEDIA_ROOT, self.get_image_path(path,''))))
    
    def parse_date(self, date_str):
        formats = [
            "%Y-%m-%d %H:%M:%S",  # 2025-03-14 01:17:00
            "%Y-%m-%dT%H:%M:%S",  # 2025-03-14T01:17:00
            "%Y-%m-%dT%H:%M",     # 2025-03-14T01:17
            "%d-%m-%Y %H:%M:%S",  # 14-03-2025 01:17:00
            "%m/%d/%Y %H:%M",     # 03/14/2025 01:17
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue  # Try next format
        
        raise ValueError("Invalid date format!")

    def is_mobile_email_available(self, mobile: str, email: str, unique_id=None):
        franchise_q = Franchise.objects.all()
        customer_q = Customer.objects.all()
        login_q = Login.objects.all()

        # update ke time current record ignore karo
        if unique_id:
            franchise_q = franchise_q.exclude(unique_id=unique_id)
            customer_q = customer_q.exclude(unique_id=unique_id)
            login_q = login_q.exclude(table_id=unique_id)

        if (
            franchise_q.filter(mobile=mobile).exists() or
            customer_q.filter(mobile=mobile).exists() or
            login_q.filter(mobile_number=mobile).exists()
        ):
            return False

        if email:
            if (
                franchise_q.filter(email=email).exists() or
                customer_q.filter(email=email).exists() or
                login_q.filter(email=email).exists()
            ):
                return False

        return True

    def save_document(self, file, base_dir, prefix):
        ext = os.path.splitext(file.name)[1]
        filename = f"{prefix}_{random.randint(100000,999999)}{ext}"
        full_path = os.path.join(base_dir, filename)

        with open(full_path, "wb+") as destination:
            for chunk in file.chunks():
                destination.write(chunk)

        return filename
    
class PasswordUtility:
    def generic_reset_link_validation(self, model_class, unique_id):
        context = {'unique_id': unique_id,'is_valid': False,'message': 'N/A'}
        
        if not unique_id:
            context['message'] = 'The URL you tried to use is either incorrect or no longer valid. Please request a new password reset.'

        try:
            reset_obj = model_class.objects.get(unique_id=unique_id)

            if reset_obj.password_changed == "Yes" or timezone.now() > reset_obj.valid_till or reset_obj.link_status == "Expired":
                context['message'] = 'The URL you tried to use is either incorrect or no longer valid. Please request a new password reset.'
            else:
                context['is_valid'] = True
        except model_class.DoesNotExist:
            context['message'] = 'Invalid or Broken Link!'

        return context

class RandomIdGenerate:
    def generateUID(self):
        unique_id = secrets.randbits(64) 
        return unique_id
    
    def generate_short_uuid(self,trim_char):
        # reference_id = str(uuid.uuid4())  # Generates a unique identifier
        # print(reference_id)
        
        # reference_id = base64.urlsafe_b64encode(uuid.uuid4().bytes).decode('utf-8').rstrip('=')
        # return reference_id[:trim_char]

        # Generate a UUID4
        unique_uuid = uuid.uuid4().hex  # Convert UUID4 to a hex string
        # Hash the UUID using SHA-256
        hashed_uuid = hashlib.sha256(unique_uuid.encode('utf-8')).hexdigest()
        # Use only alphanumeric characters (Base62) from the hash
        alphabet = string.ascii_letters + string.digits  # A-Z, a-z, 0-9
        alphanumeric_id = ''.join([alphabet[int(char, 16) % 62] for char in hashed_uuid])[:trim_char]
        return alphanumeric_id

    def generate_order_id(self,prefix="order_", length=14):
        characters = string.ascii_letters  # Uppercase + Lowercase letters
        random_part = ''.join(secrets.choice(characters) for _ in range(length))
        return f"{prefix}{random_part}"

# rand_obj = RandomIdGenerate()
# print(rand_obj.generateUID())
# print("Short data ::",rand_obj.generate_short_uuid(10))

class Validation:
    def validate_mobile(self,mobile):
        if not mobile.isdigit():
            return "Username should be numeric only"
        if len(mobile)!=10:
            return "Mobile number should be 10 character long"
        return 1
    
    def validate_digit(self,**kwargs):
        invalid_vars = [var for var, value in kwargs.items() if not str(value).isdigit()]
    
        if invalid_vars:
            return f"{', '.join(invalid_vars)} wrong input data."
        return 1
       
    def validate_amount(self,amount):
        try:
            amount = Decimal(amount)  # Convert to Decimal
        except InvalidOperation:
            return "Invalid amount format."
        
        if amount <= 0:
            return "Amount must be greater than zero."
        
        return 1

    def validate_floating_number(self,data):
        try:
            data = Decimal(data)  # Convert to Decimal
        except InvalidOperation:
            return "Invalid format."
        
        return 1

    def validate_alphanumeric(self,**kwargs):
        invalid_vars = [var for var, value in kwargs.items() if not str(value).isalnum()]
    
        if invalid_vars:
            return f"{', '.join(invalid_vars)} must be alphanumeric."
        return 1
    
    def validate_alpha_with_space(self,**kwargs):
        invalid_vars = [var for var, value in kwargs.items() if not re.fullmatch(r"[A-Za-z ]+", value)]
    
        if invalid_vars:
            return f"{', '.join(invalid_vars)} must contain alphabates only."
        return 1
    
    def validate_access(self,access):
        accLst = ['Granted','Blocked']
        if access not in accLst:
            return "Wrong Access Data"
        return 1

    def validate_yesno(self,**kwargs):
        Lst = ['Yes','No']
        invalid_vars = [var for var, value in kwargs.items() if not Lst]
    
        if invalid_vars:
            return f"{', '.join(invalid_vars)} wrong data."
        return 1
    
    def validate_image(self,file,imageType,imageWidth,imageHeight):
        errors = []
        extension = os.path.splitext(str(file))[1]
        width, height = get_image_dimensions(file)

        if extension not in imageType:
            errors.append('Invalid file type (only jpg, jpeg, png).')

        if(imageWidth!='NA' and imageHeight!='NA'):
            if (imageWidth != width or imageHeight != height):
                errors.append('Image width and height is not matching.')

        return errors
    
    def validate_aadhaar_verhoeff(self,aadhaar_number):
        # Verhoeff Algorithm Tables
        multiplication_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 2, 3, 4, 0, 6, 7, 8, 9, 5],
            [2, 3, 4, 0, 1, 7, 8, 9, 5, 6],
            [3, 4, 0, 1, 2, 8, 9, 5, 6, 7],
            [4, 0, 1, 2, 3, 9, 5, 6, 7, 8],
            [5, 9, 8, 7, 6, 0, 4, 3, 2, 1],
            [6, 5, 9, 8, 7, 1, 0, 4, 3, 2],
            [7, 6, 5, 9, 8, 2, 1, 0, 4, 3],
            [8, 7, 6, 5, 9, 3, 2, 1, 0, 4],
            [9, 8, 7, 6, 5, 4, 3, 2, 1, 0]
        ]

        permutation_table = [
            [0, 1, 2, 3, 4, 5, 6, 7, 8, 9],
            [1, 5, 7, 6, 2, 8, 3, 0, 9, 4],
            [5, 8, 0, 3, 7, 9, 6, 1, 4, 2],
            [8, 9, 1, 6, 0, 4, 3, 5, 2, 7],
            [9, 4, 5, 3, 1, 2, 6, 8, 7, 0],
            [4, 2, 8, 6, 5, 7, 3, 9, 0, 1],
            [2, 7, 9, 3, 8, 0, 6, 4, 1, 5],
            [7, 0, 4, 6, 9, 1, 3, 2, 5, 8]
        ]

        inverse_table = [0, 4, 3, 2, 1, 5, 6, 7, 8, 9]
        """Validate Aadhaar number using Verhoeff Algorithm"""
        aadhaar_number = str(aadhaar_number)
        
        # Check if it contains only digits
        if not aadhaar_number.isdigit() or len(aadhaar_number) != 12:
            raise ValidationError("Invalid Aadhaar number. It must be 12 digits.")

        # c = 0
        # for i, digit in enumerate(reversed(aadhaar_number)):
        #     c = multiplication_table[c][permutation_table[(i + 1) % 8][int(digit)]]
        
        # if c != 0:
        #     raise ValidationError("Invalid Aadhaar number (failed checksum validation).")

    def validate_pan_entity(self,value):
        """Validate PAN format and check entity type"""
        pan_regex = r'^[A-Z]{5}[0-9]{4}[A-Z]{1}$'
        valid_entities = {'P', 'C', 'H', 'A', 'B', 'F', 'G'}

        if not re.match(pan_regex, value):
            raise ValidationError("Invalid PAN format.")
        
        if value[3] not in valid_entities:
            raise ValidationError(f"Invalid entity type '{value[3]}' in PAN.")

    def validate_email(self,value):
        """Validate email format using regex."""
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, value):
            raise ValidationError("Invalid email address format.")

    def validate_mobile_number(self,value):
        """Validate that the mobile number has exactly 10 digits."""
        mobile_regex = r'^[6-9]\d{9}$'  # Starts with 6-9 and has 10 digits
        if not re.match(mobile_regex, value):
            raise ValidationError("Invalid mobile number. Must be 10 digits starting with 6-9.")

    def validate_pincode(self,value):
        """Validate that the pincode has exactly 6 digits and starts with 1-9."""
        pincode_regex = r'^[1-9][0-9]{5}$'  # First digit 1-9, followed by 5 digits (0-9)
        if not re.match(pincode_regex, value):
            raise ValidationError("Invalid Pincode. Must be a 6-digit number starting with 1-9.")
    
    def validate_alpha(self,value):
        """Validate name format and length."""
        value = value.strip()  # Remove leading/trailing spaces

        name_regex = r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$'  # Allows letters & spaces
        if not re.match(name_regex, value):
            raise ValidationError("Invalid data. Only letters and spaces are allowed.")

        if len(value) < 2:  # Minimum length check
            raise ValidationError("Data must be at least 2 characters long.")
        
        if len(value) > 50:  # Maximum length check
            raise ValidationError("Data must not exceed 50 characters.")

    def validate_alpha_multiple_keys(self,**kwargs):
        """
        Validate multiple fields for name format (letters & spaces) and length (2-50).
        Returns a string-formatted error message.
        
        :param kwargs: Dictionary of field names and values
        :raises ValidationError: If any field fails validation
        """
        errors = {}
        name_regex = r'^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$'  # Allows letters & spaces

        for field, value in kwargs.items():
            value = value.strip()  # Remove leading/trailing spaces
            field = field.replace('_', ' ').title()
            if not re.match(name_regex, value):
                errors[field] = "Only letters and spaces are allowed."
            elif len(value) < 2:
                errors[field] = "Data must be at least 2 characters long."
            elif len(value) > 50:
                errors[field] = "Data must not exceed 50 characters."

        if errors:
            # Group fields by error messages
            grouped_errors = {}
            for field, message in errors.items():
                grouped_errors.setdefault(message, []).append(field)

            # Convert errors to a readable string
            error_messages = [
                f"{', '.join(fields)}: {message}" for message, fields in grouped_errors.items()
            ]
            
            raise ValidationError("; ".join(error_messages))  # Convert dictionary to string
        
    def validate_password(self,value):
        """Validate password strength: min 8 chars, 1 uppercase, 1 lowercase, 1 digit, 1 special char."""
        password_regex = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'

        if not re.match(password_regex, value):
            raise ValidationError(
                "Password must be at least 8 characters long, include an uppercase letter, "
                "a lowercase letter, a number, and a special character."
            )

    def validate_alpha_num_re(self,value):
        """Validate referral code: alphanumeric, 6-10 characters."""
        if not re.match(r'^[A-Za-z0-9]{6,10}$', value):
            raise ValidationError("Referral code must be 6-10 alphanumeric characters.")
        
    def validate_address(self,value):
        """Validates address (alphanumeric with common symbols like comma, dot, and hyphen)."""
        if not re.match(r'^[A-Za-z0-9\s,.-]{5,255}$', value):  
            # raise ValidationError("Enter a valid address (5-255 characters, only letters, numbers, comma, dot, and hyphen allowed).")
            raise ValidationError("Enter a valid address).")

    def validate_address_multiple_keys(self,**kwargs):
        """
        Validate multiple address fields (alphanumeric with common symbols like comma, dot, and hyphen).
        
        :param kwargs: Dictionary of field names and values
        :raises ValidationError: If any field fails validation, errors are grouped & formatted.
        """
        errors = {}
        address_regex = r'^[A-Za-z0-9\s,.-]{5,255}$'  # Allows letters, numbers, spaces, comma, dot, and hyphen

        for field, value in kwargs.items():
            field = field.replace('_', ' ').title()
            value = value.strip()  # Remove leading/trailing spaces

            if not re.match(address_regex, value):
                errors[field] = "Enter a valid address (5-255 characters, only letters, numbers, comma, dot, and hyphen allowed)."

        if errors:
            # Group fields with the same error message
            grouped_errors = {}
            for field, message in errors.items():
                grouped_errors.setdefault(message, []).append(field)

            # Convert errors to a readable string
            error_messages = [
                f"{', '.join(fields)}: {message}" for message, fields in grouped_errors.items()
            ]

            raise ValidationError("; ".join(error_messages))  # Raise error as a formatted string

    def validate_float(self,value):
        """Ensure the value is a valid float (both positive & negative allowed)."""
        try:
            float(value)  # Convert to float (raises error if invalid)
        except ValueError:
            raise ValidationError("Invalid float value.")
        
    def validate_float_multiple_keys(self,**kwargs):
        """
        Validate multiple fields to ensure they contain valid float values (both positive & negative allowed).
        
        :param kwargs: Dictionary of field names and values
        :raises ValidationError: If any field fails validation, errors are grouped & formatted.
        """
        errors = {}

        for field, value in kwargs.items():
            field = field.replace('_', ' ').title()
            try:
                float(value)  # Try converting to float
            except ValueError:
                errors[field] = "Invalid float value."

        if errors:
            # Group fields with the same error message
            grouped_errors = {}
            for field, message in errors.items():
                field = field.capitalize()
                grouped_errors.setdefault(message, []).append(field)

            # Convert errors to a readable string
            error_messages = [
                f"{', '.join(fields)}: {message}" for message, fields in grouped_errors.items()
            ]

            raise ValidationError("; ".join(error_messages))  # Raise error as a formatted string

    def validate_digits_multiple_keys(self,**fields):
        """
        Validate multiple fields to ensure they contain only digits.
        
        :param fields: Dictionary of field names and their corresponding values.
        :raises ValidationError: If any field contains non-digit characters.
        """
        digit_regex = r'^\d+$'
        errors = {}

        for field_name, value in fields.items():
            if not re.match(digit_regex, str(value)):  # Convert to string to handle integers
                errors[field_name] = f"{field_name.replace('_', ' ').title()} must contain only digits."

        if errors:
            raise ValidationError(errors)

util_obj = Utility()
valid_obj = Validation()
random_obj = RandomIdGenerate()

class DataList:
    def getAllDataByTable(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                # try:
                    limit = 10
                    if request.POST.get('limit') is not None and request.POST.get('limit') !="":
                        limit = int(request.POST['limit'])
                    
                    table_name = request.POST['type']
                    role = request.session.get("role")
                    login_id = request.session.get("login_id")
                    conditions={}
                    page = 1
                    start = 0
                    if request.POST.get('page') is not None and int(request.POST.get('page')) > 1:
                        page = int(request.POST['page'])
                        start= ((page - 1) * limit)
                    
                    if table_name == "metal_purity_price":
                        query = MetalPurityPrice.objects.select_related("metal","purity").all()
                    elif table_name == "unit":
                        query = Unit.objects.all()
                    elif table_name == "category":
                        query = Category.objects.all()
                    elif table_name == "product":
                        query = Product.objects.select_related("category","metal","metal_type","purity").all()
                    elif table_name == "image_slider":
                        query = ImageSlider.objects.all()
                    elif table_name == "customer":
                        query = Customer.objects.all()
                    elif table_name == "customer_cart_list":
                        query = Cart.objects.select_related('customer').annotate(total_items=Count('cart_items__id'), total_quantity=Sum('cart_items__quantity'), cart_value=Sum('cart_items__total')).all()
                    elif table_name == "customer_order_list":
                        query = Order.objects.select_related('customer').all()
                    elif table_name == "stock":
                        query = Stock.objects.select_related('product').all()
                    elif table_name == "stock_movement":
                        query = StockMovement.objects.select_related('product').all()
                    elif table_name == "trading_user":
                        # 🔹 SUPER ADMIN
                        if role == 1 or role == 5:
                            # query = Franchise.objects.filter(franchise_model="SMRA")
                            query = Franchise.objects.all()
                            if request.POST.get('franchise_model'):
                                conditions['franchise_model__exact'] = request.POST.get("franchise_model")
                        else:
                            # 🔹 Logged-in franchise
                            login = Login.objects.get(id=login_id)

                            # table_id me franchise ka unique_id stored hai
                            parent_franchise = Franchise.objects.get(
                                unique_id=login.table_id
                            )

                            next_model = ROLE_FRANCHISE_MAP.get(role)

                            query = Franchise.objects.filter(
                                parent_id=parent_franchise.id,
                                franchise_model=next_model
                            )
                    elif table_name == "contact_messages":
                        query = ContactMessage.objects.all()
                    elif table_name == "portal_user":
                        query = Login.objects.filter(role__role_name="Admin")
                    elif table_name == "registration_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('referral_code')).values('holder_name')[:1]
                        last_login = CustomerLoginReport.objects.filter(customer=OuterRef('unique_id')).order_by('-login_date_time')
                        first_address = CustomerAddress.objects.filter(customer=OuterRef('unique_id')).order_by('id')

                        query = Customer.objects.annotate(
                            referral_holder_name=Subquery(franchise_holder),
                            last_login_date_time=Subquery(last_login.values('login_date_time')[:1]),
                            last_latitude=Subquery(last_login.values('latitude')[:1]),
                            last_longitude=Subquery(last_login.values('longitude')[:1]),
                            state=Subquery(first_address.values('state')[:1])
                        )
                    elif table_name == "wallet_recharge_report":
                        # query = WalletRechargeHistory.objects.select_related("customer","membership_allocated","order").filter(status="Success")
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('customer__referral_code')).values('holder_name')[:1]
                        query = WalletRechargeHistory.objects.select_related("customer","membership_allocated","order").annotate(referral_holder_name=Subquery(franchise_holder))
                    elif table_name == "first_recharge_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('customer__referral_code')).values('holder_name')[:1]
                        first_recharge = WalletRechargeHistory.objects.filter(customer=OuterRef("customer"),status="Success").order_by("created_at")
                        query = WalletRechargeHistory.objects.filter(id=Subquery(first_recharge.values("id")[:1])).select_related("customer","membership_allocated","order").annotate(referral_holder_name=Subquery(franchise_holder))
                    elif table_name == "transaction_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('customer__referral_code')).values('holder_name')[:1]
                        query = CustomerTransaction.objects.filter(transaction_type="BUY").prefetch_related("sell_transactions").select_related("customer","membership").annotate(referral_holder_name=Subquery(franchise_holder))
                    elif table_name == "customer_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('referral_code')).values('holder_name')[:1]
                        last_login = CustomerLoginReport.objects.filter(customer=OuterRef('unique_id')).order_by('-login_date_time')

                        query = Customer.objects.select_related(
                            'customertradingaccount',
                            'customertradingbankdetails',
                            'customertradingterms'
                        ).prefetch_related(
                            'customeraddress_set',
                            'customertradingdocuments_set'
                        ).annotate(
                            referral_holder_name=Subquery(franchise_holder),
                            last_login_date_time=Subquery(last_login.values('login_date_time')[:1]),
                            last_latitude=Subquery(last_login.values('latitude')[:1]),
                            last_longitude=Subquery(last_login.values('longitude')[:1]),
                        ).all()
                    elif table_name == "order_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('customer__referral_code')).values('holder_name')[:1]
                        query = Order.objects.select_related("customer").prefetch_related("orderdetails_set","orderstatus_set").annotate(referral_holder_name=Subquery(franchise_holder))
                    elif table_name=="inactive_no_recharge":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('referral_code')).values('holder_name')[:1]
                        recharge_exists = WalletRechargeHistory.objects.filter(
                            customer=OuterRef('pk'),
                            status="Success"
                        )

                        query = Customer.objects.select_related(
                            'customertradingaccount'
                        ).annotate(
                            has_recharge=Exists(recharge_exists),
                            referral_holder_name=Subquery(franchise_holder),
                        ).filter(
                            trading="ON",
                            has_recharge=False
                        )
                    elif table_name=="inactive_customers":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('referral_code')).values('holder_name')[:1]

                        last_login = CustomerLoginReport.objects.filter(
                            customer=OuterRef('unique_id')
                        ).order_by('-login_date_time')

                        last_txn = CustomerTransaction.objects.filter(
                            customer=OuterRef('unique_id')
                        ).order_by('-created_at')

                        query = Customer.objects.annotate(
                            referral_holder_name=Subquery(franchise_holder),
                            last_login_date=Subquery(last_login.values('login_date_time')[:1]),
                            last_txn_date=Subquery(last_txn.values('created_at')[:1])
                        ).filter(
                                trading="ON"
                            )
                    elif table_name == "customer_transfer_report":
                        query = ReferralHistory.objects.select_related("customer")
                    elif table_name == "withdrawal_report":
                        franchise_holder = Franchise.objects.filter(referral_id=OuterRef('customer__referral_code')).values('holder_name')[:1]
                        query = WithdrawalRequest.objects.select_related("customer","customer__customertradingbankdetails").annotate(referral_holder_name=Subquery(franchise_holder))
                    
                    search_tearm = ''
                    if(request.POST['query'] != ''):
                        search_tearm = request.POST['query']

                        if table_name=="metal_purity_price":
                            query=query.filter(Q(price_per_10_gm__icontains=search_tearm) | Q(metal__metal_name__icontains=search_tearm) | Q(purity__purity__icontains=search_tearm))
                        elif table_name=="unit":
                            query=query.filter(Q(unit_name__icontains=search_tearm))
                        elif table_name=="category":
                            query=query.filter(Q(name__icontains=search_tearm))
                        elif table_name=="product":
                            query=query.filter(Q(total_price__icontains=search_tearm) | Q(metal__metal_name__icontains=search_tearm) | Q(purity__purity__icontains=search_tearm) | Q(metal_type__type__icontains=search_tearm) | Q(category__name__icontains=search_tearm) | Q(name__icontains=search_tearm) | Q(size__icontains=search_tearm) | Q(hot_sale__icontains=search_tearm))
                        elif table_name=="image_slider":
                            query=query.filter(Q(image_type__icontains=search_tearm))
                        elif table_name=="customer":
                            query=query.filter(Q(name__icontains=search_tearm) | Q(mobile__icontains=search_tearm) | Q(email__icontains=search_tearm) | Q(aadhaar_number__icontains=search_tearm) | Q(pan_number__icontains=search_tearm) | Q(referral_code__icontains=search_tearm))
                        elif table_name=="customer_cart_list":
                            query=query.filter(Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(cart_status__icontains=search_tearm))
                        elif table_name=="customer_order_list":
                            query=query.filter(Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(order_status__icontains=search_tearm) | Q(order_id__icontains=search_tearm) | Q(order_number__icontains=search_tearm) | Q(razorpay_order_id__icontains=search_tearm) | Q(razorpay_payment_id__icontains=search_tearm) | Q(payment_status__icontains=search_tearm))
                        elif table_name=="stock":
                            query=query.filter(Q(quantity__icontains=search_tearm) | Q(product__name__icontains=search_tearm))
                        elif table_name=="stock_movement":
                            query=query.filter(Q(quantity__icontains=search_tearm) | Q(movement_type__icontains=search_tearm) | Q(reference__icontains=search_tearm) | Q(product__name__icontains=search_tearm))
                        elif table_name=="trading_user":
                            query=query.filter(Q(referral_id__icontains=search_tearm) | Q(franchise_name__icontains=search_tearm) | Q(holder_name__icontains=search_tearm) | Q(mobile__icontains=search_tearm) | Q(email__icontains=search_tearm))
                        elif table_name=="contact_messages":
                            query=query.filter(Q(name__icontains=search_tearm) | Q(phone__icontains=search_tearm) | Q(email__icontains=search_tearm))
                        elif table_name=="portal_user":
                            query=query.filter(Q(name__icontains=search_tearm) | Q(mobile_number__icontains=search_tearm) | Q(email__icontains=search_tearm) | Q(password_text__icontains=search_tearm))
                        elif table_name=="registration_report":
                            query=query.filter(Q(name__icontains=search_tearm) | Q(mobile__icontains=search_tearm) | Q(state__icontains=search_tearm) | Q(last_latitude__icontains=search_tearm) | Q(last_longitude__icontains=search_tearm))
                        elif table_name=="wallet_recharge_report" or table_name=="first_recharge_report":
                            query=query.filter(Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(razorpay_payment_id__icontains=search_tearm) | Q(order__razorpay_order_id__icontains=search_tearm))
                        elif table_name=="transaction_report":
                            query=query.filter(Q(transaction_id__icontains=search_tearm) | Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(metal_type__icontains=search_tearm) | Q(transaction_type__icontains=search_tearm) | Q(order_type__icontains=search_tearm) | Q(sell_transactions__profit_loss__icontains=search_tearm))
                        elif table_name=="customer_report":
                            query=query.filter(
                                Q(name__icontains=search_tearm) |
                                Q(mobile__icontains=search_tearm) |
                                Q(email__icontains=search_tearm) |
                                Q(aadhaar_number__icontains=search_tearm) |
                                Q(pan_number__icontains=search_tearm) |
                                Q(referral_code__icontains=search_tearm) |
                                Q(referral_holder_name__icontains=search_tearm) |
                                Q(last_latitude__icontains=search_tearm) | 
                                Q(last_longitude__icontains=search_tearm) |
                                Q(customeraddress__city__icontains=search_tearm) |
                                Q(customeraddress__state__icontains=search_tearm) |
                                Q(customertradingdocuments__doc_type__icontains=search_tearm) |
                                Q(customertradingaccount__status__icontains=search_tearm) |
                                Q(customertradingaccount__account_type__icontains=search_tearm) |
                                Q(customertradingbankdetails__bank_name__icontains=search_tearm) |
                                Q(customertradingbankdetails__account_number__icontains=search_tearm)
                            ).distinct()
                        elif table_name=="order_report":
                            query = query.filter(
                                Q(order_number__icontains=search_tearm) |
                                Q(order_id__icontains=search_tearm) |
                                Q(customer__name__icontains=search_tearm) |
                                Q(customer__mobile__icontains=search_tearm) |
                                Q(customer__email__icontains=search_tearm) |
                                Q(customer__referral_code__icontains=search_tearm) |
                                Q(referral_holder_name__icontains=search_tearm) |
                                Q(orderdetails__product_name__icontains=search_tearm) |
                                Q(orderdetails__category_name__icontains=search_tearm) |
                                Q(orderdetails__prd_detail_id__icontains=search_tearm) |
                                Q(orderdetails__order_status__icontains=search_tearm) |
                                Q(orderstatus__order_status__icontains=search_tearm) |
                                Q(payment_status__icontains=search_tearm) |
                                Q(razorpay_order_id__icontains=search_tearm) |
                                Q(razorpay_payment_id__icontains=search_tearm) |
                                Q(city__icontains=search_tearm) |
                                Q(state__icontains=search_tearm) |
                                Q(pincode__icontains=search_tearm) |
                                Q(address_line_1__icontains=search_tearm) |
                                Q(address_line_2__icontains=search_tearm)
                            ).distinct()
                        elif table_name=="inactive_no_recharge":
                            query = query.filter(
                                Q(name__icontains=search_tearm) |
                                Q(mobile__icontains=search_tearm) |
                                Q(email__icontains=search_tearm) | 
                                Q(referral_code__icontains=search_tearm) |
                                Q(referral_holder_name__icontains=search_tearm)
                            )
                        elif table_name=="inactive_customers":
                            query = query.filter(
                                Q(name__icontains=search_tearm) |
                                Q(mobile__icontains=search_tearm) |
                                Q(email__icontains=search_tearm) |
                                Q(referral_code__icontains=search_tearm) |
                                Q(referral_holder_name__icontains=search_tearm)
                            )
                        elif table_name=="customer_transfer_report":
                            query=query.filter(Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(old_referral_code__icontains=search_tearm) | Q(new_referral_code__icontains=search_tearm))
                        elif table_name=="withdrawal_report":
                            query=query.filter(Q(customer__name__icontains=search_tearm) | Q(customer__mobile__icontains=search_tearm) | Q(transaction_number__icontains=search_tearm) | Q(status__icontains=search_tearm) | Q(customer__customertradingbankdetails__bank_name__icontains=search_tearm) | Q(customer__customertradingbankdetails__account_holder_name__icontains=search_tearm) | Q(customer__customertradingbankdetails__account_number__icontains=search_tearm) | Q(customer__customertradingbankdetails__ifsc_code__icontains=search_tearm))
                        
                    from_date=''
                    to_date=''
                    if request.POST.get('from_date'):
                        from_date = request.POST.get('from_date')
                        to_date = request.POST.get('to_date')

                        if table_name in ["wallet_recharge_report", "first_recharge_report", "transaction_report"]:
                            if from_date:
                                conditions['created_at__gte'] = datetime.strptime(from_date, "%Y-%m-%d")
                            if to_date:
                                conditions['created_at__lt'] = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
                        elif table_name in ["customer_transfer_report"]:
                            if from_date:
                                conditions['transfer_date__gte'] = datetime.strptime(from_date, "%Y-%m-%d")
                            if to_date:
                                conditions['transfer_date__lt'] = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
                        elif table_name in ["withdrawal_report"]:
                            if from_date:
                                conditions['request_date__gte'] = datetime.strptime(from_date, "%Y-%m-%d")
                            if to_date:
                                conditions['request_date__lt'] = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
                        else:
                            if from_date:
                                conditions['date__gte'] = datetime.strptime(from_date, "%Y-%m-%d")
                            if to_date:
                                conditions['date__lt'] = datetime.strptime(to_date, "%Y-%m-%d") + timedelta(days=1)
                            
                    # print('condition',conditions)

                    if request.POST.get('access'):
                        access = request.POST['access']
                        if(access!="" and access!="All"):
                            if table_name == "customer_cart_list":
                                conditions['cart_status__exact']=access
                            elif table_name == "customer_order_list":
                                conditions['payment_status__exact']=access 
                            else:   
                                conditions['access__exact']=access

                    if table_name == "stock_movement":
                        conditions['product__unique_id__exact'] = request.session.get("product_id")

                    if role == 4 and table_name == "customer":
                        login = Login.objects.get(id=login_id)
                        parent_franchise = Franchise.objects.get(unique_id=login.table_id)
                        referral_id = parent_franchise.referral_id
                        
                        conditions['referral_code__exact'] = referral_id

                    if table_name == "inactive_customers":
                        days = int(request.POST.get("days") or 15)
                        conditions_q = Q(last_login_date__lt=timezone.now() - timedelta(days=days)) | Q(last_txn_date__lt=timezone.now() - timedelta(days=days)) | Q(last_login_date__isnull=True)
                        query = query.filter(conditions_q)

                    if(len(conditions)>0):
                        query=query.filter(**conditions)
                    
                    query=query.order_by('-id')

                    # print(query)

                    # filter_query = query[start: start + limit]
                    export = request.POST.get("export")

                    if export == "excel":
                        filter_query = query
                    else:
                        filter_query = query[start: start + limit]

                    total_data = len(query)
                    total_filter_data = len(filter_query)

                    table_data=[]

                    if (total_data > 0):
                        sr_no = start+1
                        for row in filter_query:
                            if table_name not in ["stock", "stock_movement", "wallet_recharge_report", "first_recharge_report","transaction_report","order_report", "customer_transfer_report", "withdrawal_report"]:
                                date=timezone.localtime(row.date).strftime('%d-%m-%Y')
                                date_time=timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')

                            if table_name not in ["customer_cart_list", "customer_order_list", "stock", "stock_movement", "contact_messages", "wallet_recharge_report", "first_recharge_report", "transaction_report","order_report", "customer_transfer_report", "withdrawal_report"]:
                                if(row.access=="Granted"):
                                    cls='success'
                                    states="checked"
                                else:
                                    cls='danger'
                                    states=""

                            if table_name in ['registration_report','wallet_recharge_report','first_recharge_report','transaction_report','customer_report','order_report','inactive_no_recharge','inactive_customers', 'withdrawal_report']:
                                referral_holder = row.referral_holder_name if row.referral_holder_name else "N/A"

                            if table_name=="metal_purity_price":
                                formatted_price = util_obj.formatPrice(row.price_per_10_gm)
                                table_data.append({'sr_no':sr_no, 'unique_id':row.unique_id, 'date':date, 'price':formatted_price, 'metal':row.metal.metal_name, 'purity':row.purity.purity, 'access':row.access, 'cls':cls,'states':states})
                            elif table_name=="unit":
                                table_data.append({'sr_no':sr_no, 'unique_id':row.unique_id, 'date':date, 'unit_name':row.unit_name, 'access':row.access, 'cls':cls,'states':states})
                            elif table_name=="category":
                                table_data.append({'sr_no':sr_no, 'unique_id':row.unique_id, 'date':date, 'name':row.name, 'image':urlPrefix+row.image, 'access':row.access, 'cls':cls,'states':states})
                            elif table_name=="product":
                                if(row.hot_sale=="Yes"):
                                    hot_cls='success'
                                else:
                                    hot_cls='danger'
                                formatted_price = util_obj.formatPrice(row.total_price)
                                table_data.append({'sr_no':sr_no, 'unique_id':row.unique_id, 'date':date, 'price':formatted_price, 'metal':row.metal.metal_name, 'purity':row.purity.purity, 'metal_type':row.metal_type.type, 'category':row.category.name, 'name':row.name, 'size':row.size, 'hot_sale':row.hot_sale, 'hot_cls':hot_cls, 'access':row.access, 'cls':cls,'states':states})
                            elif table_name=="image_slider":
                                table_data.append({'sr_no':sr_no,'unique_id':row.unique_id, 'date':date,'image_type':row.image_type, 'sequence':row.sequence, 'image':urlPrefix+row.image, 'access':row.access, 'cls':cls,'states':states})
                            elif table_name=="customer":
                                if(row.trading=="ON"):
                                    cls_trade='success'
                                    states_trade="checked"
                                else:
                                    cls_trade='danger'
                                    states_trade=""

                                btn = "No"
                                status_cls='info'
                                status_txt='No Status'
                                demo_account='N/A'
                                cls_account='warning'
                                states_account=''

                                trading_account = CustomerTradingAccount.objects.filter(customer_id=row.id,trading_enabled='ON',is_blocked='No').first()
                                if trading_account:
                                    status_txt=trading_account.status
                                    if(trading_account.status=="Approved"):
                                        status_cls='success'
                                    elif(trading_account.status=="Pending"):
                                        status_cls='warning'
                                        btn = "Yes"
                                    elif(trading_account.status=="Rejected"):
                                        status_cls='danger'

                                    if(trading_account.account_type=="DEMO"):
                                        cls_account='success'
                                        states_account="checked"
                                        demo_account='DEMO'
                                    else:
                                        cls_account='danger'
                                        states_account=""
                                        demo_account='LIVE'

                                table_data.append({'sr_no':sr_no,'unique_id':row.unique_id, 'date':date,'customer_name':row.name, 'mobile_number':row.mobile, 'email':row.email, 'access':row.access, 'cls':cls,'states':states, 'mac_reset_count':row.mac_reset_count,'trading':row.trading, 'cls_trade':cls_trade,'states_trade':states_trade,'status_cls':status_cls,'btn':btn,'status_txt':status_txt, 'cls_account':cls_account, 'states_account':states_account, 'demo_account':demo_account, 'referral_code':row.referral_code})
                            elif table_name=="customer_cart_list":
                                if row.cart_status=="Pending":
                                    cls='primary'
                                elif row.cart_status=="Processed":
                                    cls='success'

                                formatted_price = util_obj.formatPrice(row.cart_value)

                                table_data.append({'sr_no':sr_no,'cart_id':row.cart_id, 'date':date,'customer_name':row.customer.name, 'mobile_number':row.customer.mobile, 'total_items':row.total_items, 'total_quantity':row.total_quantity, 'cart_value':formatted_price, 'cart_status':row.cart_status, 'cls':cls})
                            elif table_name=="customer_order_list":
                                if row.order_status=="Placed":
                                    cls='primary'
                                elif row.order_status=="Approved":
                                    cls='warning'
                                elif row.order_status=="Processed":
                                    cls='danger'
                                elif row.order_status=="Dispatched":
                                    cls='success'

                                pay_cls = 'warning'
                                if row.payment_status == 'Success':
                                    pay_cls = 'success'
                                elif row.payment_status == 'Failed':
                                    pay_cls = 'danger'

                                formatted_price = util_obj.formatPrice(row.sub_total)

                                invoice_url = domainURLPortal + 'download_invoice/' + row.order_id + '/inline'

                                table_data.append({'sr_no':sr_no,'order_number':row.order_number, 'order_id':row.order_id, 'date':date,'customer_name':row.customer.name, 'mobile_number':row.customer.mobile, 'total_items':row.total_items, 'total_quantity':row.total_quantity, 'sub_total':formatted_price, 'order_status':row.order_status, 'cls':cls, 'razorpay_order_id':row.razorpay_order_id, 'razorpay_payment_id':row.razorpay_payment_id, 'payment_status':row.payment_status, 'pay_cls':pay_cls, 'invoice_url':invoice_url})
                            elif table_name=="stock":
                                last_updated = timezone.localtime(row.last_updated).strftime('%d-%m-%Y @ %I:%M %p')
                                table_data.append({'sr_no':sr_no, 'product':row.product.unique_id, 'product_name':row.product.name, 'quantity':row.quantity, 'last_updated':last_updated})
                            elif table_name=="stock_movement":
                                movement_date = timezone.localtime(row.movement_date).strftime('%d-%m-%Y @ %I:%M %p')
                                table_data.append({'sr_no':sr_no, 'product':row.product.unique_id, 'product_name':row.product.name, 'quantity':row.quantity, 'movement_date':movement_date, 'movement_type':row.movement_type, 'reference':row.reference})
                            elif table_name=="trading_user":
                                roleAccess = False
                                if role!=None and role==1:
                                    roleAccess = True
                                btn = "No"
                                if(row.status=="Approved"):
                                    status_cls='success'
                                elif(row.status=="Pending"):
                                    status_cls='warning'
                                    btn = "Yes"
                                elif(row.status=="Rejected"):
                                    status_cls='danger'

                                table_data.append({'sr_no':sr_no,'unique_id':row.unique_id, 'date':date,'referral_id':row.referral_id, 'franchise_name':row.franchise_name, 'holder_name':row.holder_name, 'mobile':row.mobile, 'email':row.email, 'access':row.access, 'cls':cls,'states':states,'status':row.status,'status_cls':status_cls,'btn':btn,'roleAccess':roleAccess})
                            elif table_name=="contact_messages":
                                # print("DB value:", row.date)
                                # print("Local:", timezone.localtime(row.date))
                                table_data.append({'sr_no':sr_no, 'date':date_time, 'name':row.name, 'phone':row.phone, 'email':row.email, 'message':row.message})
                            elif table_name=="portal_user":
                                table_data.append({'sr_no':sr_no,'unique_id':row.table_id, 'date':date_time, 'name':row.name, 'mobile_number':row.mobile_number, 'email':row.email, 'access':row.access, 'cls':cls,'states':states,'password':row.password_text})
                            elif table_name=="registration_report":
                                last_login = 'N/A'
                                latitude = 'N/A'
                                longitude = 'N/A'
                                
                                if row.last_login_date_time:
                                    last_login = timezone.localtime(row.last_login_date_time).strftime('%d-%m-%Y @ %I:%M %p')
                                    latitude = row.last_latitude
                                    longitude = row.last_longitude

                                table_data.append({'sr_no': sr_no,'unique_id': row.unique_id,'date': date_time,'customer_name': row.name,'mobile_number': row.mobile,'email': row.email,'last_login': last_login,'latitude': latitude,'longitude': longitude,'state': row.state,'access': row.access,'cls': cls,'states': states,'referral_code': row.referral_code,'referral_holder_name': referral_holder})
                            elif table_name=="wallet_recharge_report" or table_name=="first_recharge_report":
                                date_time=timezone.localtime(row.customer.date).strftime('%d-%m-%Y @ %I:%M %p')
                                transaction_date=timezone.localtime(row.created_at).strftime('%d-%m-%Y @ %I:%M %p')

                                table_data.append({'sr_no': sr_no,'date': date_time,'customer_name': row.customer.name,'mobile_number': row.customer.mobile,'email': row.customer.email,'amount': row.amount,'membership': row.membership_allocated.level,'razorpay_payment_id': row.razorpay_payment_id, 'razorpay_order_id': row.order.razorpay_order_id, 'transaction_date': transaction_date,'status':row.status,'referral_code': row.customer.referral_code,'referral_holder_name': referral_holder})
                            elif table_name=="transaction_report":
                                sell = row.sell_transactions.first()

                                sell_price = 0
                                sell_date = ""
                                pnl = ""
                                pnl_amount = 0

                                if sell:
                                    sell_price = float(sell.market_amount)
                                    pnl = sell.profit_loss
                                    pnl_amount = float(sell.profit_loss_amount)
                                    sell_date = timezone.localtime(sell.created_at).strftime('%d-%m-%Y @ %I:%M %p')

                                buy_date = timezone.localtime(row.created_at).strftime('%d-%m-%Y @ %I:%M %p')

                                table_data.append({
                                    "sr_no": sr_no,
                                    "transaction_id": row.transaction_id,
                                    "customer_name": row.customer.name,
                                    "mobile_number": row.customer.mobile,
                                    'referral_code': row.customer.referral_code,
                                    'referral_holder_name': referral_holder,

                                    "metal_type": row.metal_type,
                                    "order_type": row.order_type,

                                    "quantity": row.quantity_gm,

                                    "buy_price": float(row.market_amount),
                                    "sell_price": sell_price,

                                    "invested_amount": float(row.order_amount),

                                    "profit_loss": pnl,
                                    "pnl_amount": pnl_amount,

                                    "buy_date": buy_date,
                                    "sell_date": sell_date,

                                    "sold_via": sell.sold_via if sell else "",
                                })
                            elif table_name=="customer_report":
                                addresses = row.customeraddress_set.all()
                                address_list = []

                                add_sr_no = 1
                                for addr in addresses:
                                    full_address = f"Address {add_sr_no}:: {addr.address_line_1}, {addr.address_line_2}, {addr.state}, {addr.city} - {addr.pincode}"
                                    address_list.append(full_address)
                                    add_sr_no += 1

                                if export == "excel":
                                    address_str = " || ".join(address_list) if address_list else "N/A"
                                else:
                                    address_str = "<br/>".join(address_list) if address_list else "N/A"

                                docs = row.customertradingdocuments_set.all()
                                doc_list = []

                                for d in docs:
                                    doc = f"{d.doc_type}:: {urlPrefix}{d.file_path}"
                                    doc_list.append(doc)

                                if export == "excel":
                                    doc_str = " || ".join(doc_list) if doc_list else "N/A"
                                else:
                                    doc_str = "<br/>".join(doc_list) if doc_list else "N/A"

                                trading_account = getattr(row, 'customertradingaccount', None)

                                bank = getattr(row, 'customertradingbankdetails', None)

                                bank_name = bank.bank_name if bank else "N/A"
                                account_holder_name = bank.account_holder_name if bank else "N/A"
                                account_number = bank.account_number if bank else "N/A"
                                ifsc = bank.ifsc_code if bank else "N/A"
                                branch_name = bank.branch_name if bank else "No"

                                terms = getattr(row, 'customertradingterms', None)
                                terms_status = terms.accepted if terms else "No"

                                last_login = 'N/A'
                                latitude = 'N/A'
                                longitude = 'N/A'
                                
                                if row.last_login_date_time:
                                    last_login = timezone.localtime(row.last_login_date_time).strftime('%d-%m-%Y @ %I:%M %p')
                                    latitude = row.last_latitude
                                    longitude = row.last_longitude

                                table_data.append({
                                    'sr_no': sr_no,
                                    'date': date_time,
                                    'customer_name': row.name,
                                    'mobile_number': row.mobile,
                                    'email': row.email,
                                    'referral_code': row.referral_code,
                                    'referral_holder_name': referral_holder,
                                    'aadhaar_number': row.aadhaar_number,
                                    'pan_number': row.pan_number,
                                    'addresses': address_str,
                                    'documents': doc_str,
                                    'access': row.access,
                                    'trading': row.trading,
                                    'trading_status': trading_account.status,
                                    'account_type': trading_account.account_type,
                                    'bank_name': bank_name,
                                    'account_holder_name': account_holder_name,
                                    'account_number': account_number,
                                    'ifsc_code': ifsc,
                                    'branch_name': branch_name,
                                    'last_login': last_login,
                                    'latitude': latitude,
                                    'longitude': longitude
                                })
                            elif table_name=="order_report":
                                order_date = timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')

                                # 🔹 All statuses fetch (already prefetched)
                                all_statuses = row.orderstatus_set.all()

                                # 🔹 Product-wise status mapping
                                product_status_map = {}

                                for s in all_statuses:
                                    if s.prd_detail_id not in product_status_map:
                                        product_status_map[s.prd_detail_id] = []

                                    formatted_date = timezone.localtime(s.date).strftime('%d-%m-%Y @ %I:%M %p')
                                    product_status_map[s.prd_detail_id].append(
                                        f"{s.order_status} ({formatted_date})"
                                    )

                                # 🔹 Order Details Loop
                                order_details = row.orderdetails_set.all()

                                # 🔥 SMART FILTER (ONLY IF PRODUCT MATCH)
                                if search_tearm:
                                    product_filtered = order_details.filter(
                                        Q(product_name__icontains=search_tearm) |
                                        Q(category_name__icontains=search_tearm) |
                                        Q(prd_detail_id__icontains=search_tearm) |
                                        Q(order_status__icontains=search_tearm)
                                    )

                                    if product_filtered.exists():
                                        order_details = product_filtered

                                total_data = total_filter_data = order_details.count()

                                for item in order_details:

                                    # ✅ Product specific status
                                    status_history_list = product_status_map.get(item.prd_detail_id, [])
                                    status_history = " | ".join(status_history_list) if status_history_list else "NA"

                                    table_data.append({
                                        'sr_no': sr_no,

                                        # 🔥 ORDER
                                        'order_number': row.order_number,
                                        'order_id': row.order_id,
                                        'order_date': order_date,

                                        # 🔥 CUSTOMER
                                        'customer_name': row.customer.name if row.customer else "N/A",
                                        'mobile': row.customer.mobile if row.customer else "N/A",
                                        'email': row.customer.email if row.customer else "N/A",
                                        'referral_code': row.customer.referral_code,
                                        'referral_holder_name': referral_holder,

                                        # 🔥 PRODUCT
                                        'product_detail_id': item.prd_detail_id,
                                        'product_name': item.product_name,
                                        'category': item.category_name,
                                        'quantity': item.quantity,
                                        'price': float(item.price),
                                        'total': float(item.total),

                                        'total_items':float(row.total_items), 
                                        'total_quantity':float(row.total_quantity), 
                                        'sub_total':float(row.sub_total),  

                                        # 🔥 CORRECT STATUS (product-wise)
                                        'product_status': item.order_status,
                                        'status_history': status_history,

                                        'remark':row.remark,

                                        # 🔥 PAYMENT
                                        'razorpay_order_id':row.razorpay_order_id, 
                                        'razorpay_payment_id':row.razorpay_payment_id, 
                                        'payment_status':row.payment_status,

                                        # 🔥 ADDRESS
                                        'address_name':row.address_name, 
                                        'address_mobile':row.address_mobile, 
                                        'pincode':row.pincode, 
                                        'postoffice':row.postoffice, 
                                        'state':row.state, 
                                        'city':row.city, 
                                        'district':row.district, 
                                        'region':row.region, 
                                        'address_line_1':row.address_line_1, 
                                        'address_line_2':row.address_line_2,
                                    })
                            elif table_name=="inactive_no_recharge":
                                table_data.append({
                                    'sr_no': sr_no,
                                    'date': date_time,
                                    'customer_name': row.name,
                                    'mobile': row.mobile,
                                    'email': row.email,
                                    'referral_code': row.referral_code,
                                    'referral_holder_name': referral_holder,
                                    'trading': row.trading,
                                    'status': "No Recharge",
                                })
                            elif table_name=="inactive_customers":
                                last_login = "N/A"
                                if row.last_login_date:
                                    last_login = timezone.localtime(row.last_login_date).strftime('%d-%m-%Y @ %I:%M %p')

                                last_txn = "N/A"
                                if row.last_txn_date:
                                    last_txn = timezone.localtime(row.last_txn_date).strftime('%d-%m-%Y @ %I:%M %p')

                                # 🔥 calculate days inactive
                                days_inactive = "N/A"
                                if row.last_login_date:
                                    days_inactive = (timezone.now() - row.last_login_date).days

                                table_data.append({
                                    'sr_no': sr_no,
                                    'date': date_time,
                                    'customer_name': row.name,
                                    'mobile': row.mobile,
                                    'email': row.email,
                                    'referral_code': row.referral_code,
                                    'referral_holder_name': referral_holder,
                                    'last_login': last_login,
                                    'last_transaction': last_txn,
                                    'days_inactive': days_inactive,
                                })
                            elif table_name=="customer_transfer_report":
                                date_time=timezone.localtime(row.customer.date).strftime('%d-%m-%Y @ %I:%M %p')
                                transfer_date=timezone.localtime(row.transfer_date).strftime('%d-%m-%Y @ %I:%M %p')

                                table_data.append({'sr_no': sr_no, 'date': date_time, 'customer_name': row.customer.name, 'mobile_number': row.customer.mobile, 'old_referral_code': row.old_referral_code, 'new_referral_code': row.new_referral_code, 'reason_for_transfer': row.reason_for_transfer, 'transfer_date': transfer_date})
                            elif table_name=="withdrawal_report":
                                date_time=timezone.localtime(row.customer.date).strftime('%d-%m-%Y @ %I:%M %p')
                                request_date=timezone.localtime(row.request_date).strftime('%d-%m-%Y @ %I:%M %p')
                                action_date=timezone.localtime(row.action_date).strftime('%d-%m-%Y @ %I:%M %p') if row.action_date else 'N/A'
                                remark = row.remark if row.remark else 'N/A'
                                transaction_number = row.transaction_number if row.transaction_number else 'N/A'

                                status_cls = None
                                btn = None
                                if(row.status=="APPROVED"):
                                    status_cls='success'
                                elif(row.status=="PENDING"):
                                    status_cls='warning'
                                    btn = "Yes"
                                elif(row.status=="REJECTED"):
                                    status_cls='danger'

                                table_data.append({'sr_no': sr_no,'date': date_time,'customer_name': row.customer.name,'mobile_number': row.customer.mobile,'email': row.customer.email,'unique_id': row.unique_id,'request_amount': float(row.request_amount),'service_charge': float(row.service_charge),'gst_amount': float(row.gst_amount),'total_deduction': float(row.total_deduction),'final_amount': float(row.final_amount),'status': row.status, 'status_cls': status_cls, 'btn': btn, 'transaction_number':transaction_number, 'remark':remark,'action_date':action_date,'request_date': request_date,'referral_code': row.customer.referral_code,'referral_holder_name': referral_holder, 'bank_name': row.customer.customertradingbankdetails.bank_name, 'account_holder_name': row.customer.customertradingbankdetails.account_holder_name, 'account_number': row.customer.customertradingbankdetails.account_number, 'ifsc_code': row.customer.customertradingbankdetails.ifsc_code})

                            sr_no=sr_no+1

                    total_links = math.ceil(total_data/limit)
                    paginate=self.pagination(total_links,page)
                    
                    arr = {'table_data':table_data,'page_array':paginate,'total_links':total_links,'total_data':total_data,'total_filter_data':total_filter_data}

                    return JsonResponse(arr, status=status.HTTP_200_OK,safe=False)  
                # except:
                #     return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def pagination(self, total_links, page):
        page_array = []
        
        # Agar total pages 7 ya usse kam hain, toh simple list dikhao (No dots needed)
        if total_links <= 7:
            for count in range(1, total_links + 1):
                page_array.append(count)
        else:
            # Jab total pages zyada hon tab dots ka logic:
            if page < 5:
                # Current page shuruat mein hai: 1 2 3 4 5 ... 10
                for count in range(1, 6):
                    page_array.append(count)
                page_array.append('...')
                page_array.append(total_links)
            elif page > total_links - 4:
                # Current page last mein hai: 1 ... 6 7 8 9 10
                page_array.append(1)
                page_array.append('...')
                for count in range(total_links - 4, total_links + 1):
                    page_array.append(count)
            else:
                # Current page beech mein hai: 1 ... 4 5 6 ... 10
                page_array.append(1)
                page_array.append('...')
                page_array.append(page - 1)
                page_array.append(page)
                page_array.append(page + 1)
                page_array.append('...')
                page_array.append(total_links)

        return page_array

    def changeAccess(self,request):
        if util_obj.checkSession(request):
            return util_obj.goToLogin(request)

        if request.method != 'POST' or not request.POST.get('changeAccess'):
            return util_obj.printErrorResponse_200('Invalid request')

        try:
            unique_id = request.POST.get("unique_id")
            _status   = request.POST.get("_status")
            table     = request.POST.get("table")

            if not all([unique_id, _status, table]):
                return util_obj.printErrorResponse_200('All fields are mandatory')

            if valid_obj.validate_digit(unique_id=unique_id) != 1:
                return util_obj.printErrorResponse_200('Invalid unique id')

            if valid_obj.validate_access(_status) != 1:
                return util_obj.printErrorResponse_200('Invalid access')

            new_status = "Granted" if _status == "Blocked" else "Blocked"

            if table not in TABLE_MODEL_MAP:
                return util_obj.printErrorResponse_200('Invalid table')

            app, model_name = TABLE_MODEL_MAP[table]
            Model = apps.get_model(app, model_name)

            with transaction.atomic():

                # 🔹 MAIN TABLE UPDATE
                if table == 'portal_user':
                   obj = Model.objects.select_for_update().filter(table_id=unique_id)
                else: 
                    obj = Model.objects.select_for_update().filter(unique_id=unique_id)
                if not obj.exists():
                    return util_obj.printErrorResponse_200('Record not found')

                obj.update(access=new_status)

                # 🔹 IF FRANCHISE → LOGIN ACCESS ALSO CHANGE
                if table == 'trading_user':
                    Login.objects.filter(
                        table_name='franchise',
                        table_id=unique_id
                    ).update(access=new_status)

                util_obj.activity_log(
                    request.session['login_id'],
                    request.session['logged'],
                    "Access",
                    f"{table} access changed to {new_status} ({unique_id})"
                )

            return JsonResponse(
                {'success': 1, 'message': 'Access updated successfully'},
                status=200
            )

        except Exception as e:
            return util_obj.printErrorResponse_200(str(e)) 

    def exportData(self, request):
        request.POST = request.POST.copy()
        request.POST["export"] = "excel"

        table_name = request.POST.get("type")

        response = self.getAllDataByTable(request)

        data = json.loads(response.content)

        table_data = data.get("table_data", [])

        wb = Workbook()
        ws = wb.active
        ws.title = "Report"

        if len(table_data) > 0:

            columns = EXPORT_COLUMNS.get(table_name)

            # fallback (agar mapping nahi ho)
            if not columns:
                columns = [(col, col) for col in table_data[0].keys()]

            headers = [col[0] for col in columns]
            ws.append(headers)

            for row in table_data:

                row_data = []

                for col in columns:
                    row_data.append(str(row.get(col[1], "")))

                ws.append(row_data)

        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )

        response['Content-Disposition'] = f'attachment; filename={table_name}.xlsx'

        wb.save(response)

        return response

    def changeTradingOption(self, request):
        if util_obj.checkSession(request):
            return util_obj.goToLogin(request)

        if request.method != 'POST' or not request.POST.get('changeTrade'):
            return util_obj.printErrorResponse_200('Invalid request')

        try:
            unique_id = request.POST.get("unique_id")
            trading   = request.POST.get("trading")  # current status

            if not unique_id or trading not in ['ON', 'OFF']:
                return util_obj.printErrorResponse_200('Invalid data')

            # Toggle logic
            new_status = 'ON' if trading == 'OFF' else 'OFF'

            with transaction.atomic():

                customer = Customer.objects.select_for_update().filter(unique_id=unique_id).first()
                if not customer:
                    return util_obj.printErrorResponse_200('Customer not found')

                # ================= UPDATE CUSTOMER TABLE =================
                customer.trading = new_status
                customer.save(update_fields=['trading'])

                # ================= TRADING ACCOUNT HANDLING =================
                trading_account = CustomerTradingAccount.objects.filter(customer=customer).first()
                demo_wallet_account = CustomerDemoWallet.objects.filter(customer=customer).first()

                if new_status == 'ON':

                    # CREATE only if not exists
                    if not trading_account:
                        ra = Franchise.objects.filter(referral_id=customer.referral_code).first()

                        CustomerTradingAccount.objects.create(
                            unique_id=random_obj.generateUID(),
                            customer=customer,
                            ra=ra,
                            trading_enabled='ON',
                            status='Pending',
                            is_blocked='No'
                        )
                    else:
                        trading_account.trading_enabled = 'ON'
                        trading_account.is_blocked = 'No'
                        trading_account.save(update_fields=['trading_enabled', 'is_blocked'])

                    if not demo_wallet_account:
                        CustomerDemoWallet.objects.create(
                            customer=customer,
                            balance=2000,
                            current_membership_id=1
                        )

                else:  # OFF
                    if trading_account:
                        trading_account.trading_enabled = 'OFF'
                        trading_account.is_blocked = 'Yes'
                        trading_account.save(update_fields=['trading_enabled', 'is_blocked'])

                # ================= ACTIVITY LOG =================
                util_obj.activity_log(
                    request.session['login_id'],
                    request.session['logged'],
                    "Trading",
                    f"Trading option set to {new_status} for customer {unique_id}"
                )

            return JsonResponse(
                {'success': 1, 'message': f'Trading option {new_status} successfully'},
                status=200
            )

        except Exception as e:
            return util_obj.printErrorResponse_200('Something went wrong')   

    def changeTradingAccount(self, request):
        if util_obj.checkSession(request):
            return util_obj.goToLogin(request)

        if request.method != 'POST' or not request.POST.get('changeAccountType'):
            return util_obj.printErrorResponse_200('Invalid request')

        # try:
        unique_id = request.POST.get("unique_id")
        account   = request.POST.get("account")  # current status

        if not unique_id or account not in ['DEMO', 'LIVE']:
            return util_obj.printErrorResponse_200('Invalid data')

        # Toggle logic
        new_status = 'DEMO' if account == 'LIVE' else 'LIVE'

        with transaction.atomic():

            customer = CustomerTradingAccount.objects.select_related("customer").select_for_update().filter(customer__unique_id=unique_id).first()
            if not customer:
                return util_obj.printErrorResponse_200('Customer not found')

            # ================= UPDATE CUSTOMER TABLE =================
            customer.account_type = new_status
            customer.save(update_fields=['account_type'])

            # ================= ACTIVITY LOG =================
            util_obj.activity_log(
                request.session['login_id'],
                request.session['logged'],
                "Account Type",
                f"Account Type changed to {new_status} for customer {unique_id}"
            )

        return JsonResponse(
            {'success': 1, 'message': f'Account Type changed to {new_status} successfully'},
            status=200
        )

        # except Exception as e:
        #     return util_obj.printErrorResponse_200('Something went wrong')   

class CustomerUtil:
    def get_valid_trading_customer(self, cid):
        # return Customer.objects.filter(
        #     unique_id=cid,
        #     trading='ON',
        #     access='Granted'
        # ).first()
        return CustomerTradingAccount.objects.select_related("customer").filter( 
            customer__unique_id=cid, 
            customer__trading='ON', 
            customer__access='Granted', 
            trading_enabled='ON',
            is_blocked='No' 
        ).first()

    def get_all_memberships(self):
        return MembershipMaster.objects.order_by('min_amount')

    def get_wallet_balance(self, customer, request):
        wallet_model = CustomerDemoWallet if getattr(request, "is_demo_account", False) else CustomerWallet
        wallet, _ = wallet_model.objects.get_or_create(customer=customer)
        return Decimal(wallet.balance).quantize(Decimal("0.00"), rounding=ROUND_HALF_UP)

    def get_current_membership(self, customer, request):
        wallet_model = CustomerDemoWallet if getattr(request, "is_demo_account", False) else CustomerWallet
        wallet = wallet_model.objects.select_related("current_membership").filter(customer=customer).first()
        return wallet.current_membership if wallet else None
        
    def get_pin_cache_key(self, customer_id):
        return f"PIN_SESSION:{customer_id}"
    
    def check_daily_transaction_limit(self, customer, request):
        trans_model = CustomerDemoTransaction if getattr(request, "is_demo_account", False) else CustomerTransaction
        membership = self.get_current_membership(customer, request)

        # print('trans_model',trans_model)

        if not membership:
            return False, "Membership not found"

        now = timezone.localtime()

        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        txn_count = trans_model.objects.filter(
            customer=customer,
            created_at__gte=start,
            created_at__lt=end
        ).count()

        # print('txn_count', txn_count)
        # print('membership.daily_slot', membership.daily_slot)

        if txn_count >= membership.daily_slot:
            return False, f"Daily transaction limit reached ({membership.daily_slot})"

        return True, None

class ProfileUtil:
    def mask_aadhaar(self, aadhaar):
        if not aadhaar:
            return ""
        return "XXXX XXXX " + aadhaar[-4:]


    def mask_pan(self, pan):
        if not pan:
            return ""
        return pan[:2] + "XXXXX" + pan[-3:]


    def mask_account(self, account):
        if not account:
            return ""
        return "XXXXXX" + account[-4:]

    def mask_ip(self, ip):
        if not ip:
            return ""
        parts = ip.split(".")
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.xxx.xxx"
        return ip
    
class PinResetKeys:
    @staticmethod
    def otp(customer_id):
        return f"PIN_RESET_OTP:{customer_id}"

    @staticmethod
    def attempts(customer_id):
        return f"PIN_RESET_ATTEMPTS:{customer_id}"

    @staticmethod
    def rate(customer_id):
        return f"PIN_RESET_RATE:{customer_id}"

    @staticmethod
    def lock(customer_id):
        return f"PIN_RESET_LOCK:{customer_id}"

    @staticmethod
    def session(customer_id):
        return f"PIN_RESET_SESSION:{customer_id}"
    
class InvoiceUtil:
    @staticmethod
    def money(val):
        return Decimal(val).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

    @staticmethod
    def rupees_in_words(amount):
        amount = Decimal(amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        rupees = int(amount)
        paise = int((amount - rupees) * 100)

        words = num2words(rupees, lang='en_IN').capitalize()

        if paise > 0:
            paise_words = num2words(paise, lang='en_IN')
            return f"Rupees {words} and {paise_words} paise only"

        return f"Rupees {words} only"