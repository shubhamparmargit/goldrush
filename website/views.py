from django.shortcuts import render
import re, html
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
from django.core.cache import cache
from website.models import ContactMessage
from utility.views import current_date, Utility

NAME_REGEX = r"^[A-Za-z\s]{2,50}$"
PHONE_REGEX = r"^[0-9]{10}$"
EMAIL_REGEX = r"^[^@]+@[^@]+\.[^@]+$"

util_obj = Utility()

class Pages:
    def index(self,request):
        return render(request,'website/index.html')
    
    def contact(self,request):
        return render(request,'website/contact.html')
    
    def ecomm_privacy_policy(self,request):
        return render(request,'website/ecomm-privacy-policy.html')
    
    def digital_privacy_policy(self,request):
        return render(request,'website/digital-privacy-policy.html')
    
    def refund_policy(self,request):
        return render(request,'website/refund-policy.html')
    
    def shipping_policy(self,request):
        return render(request,'website/shipping-policy.html')
    
    def app_terms_condition(self,request):
        return render(request,'website/app-terms-condition.html')
    
    def ecomm_terms_condition(self,request):
        return render(request,'website/ecomm-terms-condition.html')
    
    def digital_terms_condition(self,request):
        return render(request,'website/digital-terms-condition.html')
    
    def customer_ecomm_agreement(self,request):
        return render(request,'website/customer-ecomm-agreement.html')
    
    def customer_digital_agreement(self,request):
        return render(request,'website/customer-digital-agreement.html')
    
    def welcome_letter(self,request):
        return render(request,'website/welcome-letter.html')
    
class Enquiry:
    def contact_submit(self,request):
        if request.method != "POST":
            return JsonResponse({"success": 0, "message": "Invalid request"})

        # try:
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()
        message = request.POST.get("message", "").strip()
        honeypot = request.POST.get("website")

        ip = util_obj.getIPAddress(request)
        user_agent = request.META.get("HTTP_USER_AGENT")

        # 🛑 Bot detection
        if honeypot:
            return JsonResponse({"success": 0, "message": "Bot detected"})

        # 🛑 Rate limit (1 message / 60 sec)
        rate_key = f"contact_rate_{ip}"

        if cache.get(rate_key):
            return JsonResponse({
                "success":0,
                "message":"Please wait before sending another message."
            })

        errors = {}

        # Name validation
        if not name:
            errors["name"] = "Name is required"

        elif not re.match(NAME_REGEX, name):
            errors["name"] = "Only letters allowed"

        # Email validation
        if not email:
            errors["email"] = "Email is required"

        elif not re.match(EMAIL_REGEX, email):
            errors["email"] = "Invalid email address"

        # Phone validation
        if phone and not re.match(PHONE_REGEX, phone):
            errors["phone"] = "Invalid phone number"

        # Message validation
        if not message:
            errors["message"] = "Message is required"

        elif len(message) < 10:
            errors["message"] = "Message too short"

        elif len(message) > 1000:
            errors["message"] = "Message too long"

        if errors:
            return JsonResponse({
                "success":0,
                "errors":errors
            })

        # 🧹 sanitize (XSS protection)
        name = html.escape(name)
        email = html.escape(email)
        phone = html.escape(phone)
        message = html.escape(message)

        # print(current_date)

        with transaction.atomic():

            ContactMessage.objects.create(
                date=current_date,
                name=name,
                email=email,
                phone=phone,
                message=message,
                ip_address=ip,
                user_agent=user_agent
            )

        # set rate limit
        cache.set(rate_key, True, timeout=60)

        return JsonResponse({
            "success":1,
            "message":"Message sent successfully"
        })

        # except Exception:

        #     return JsonResponse({
        #         "success":0,
        #         "message":"Something went wrong"
        #     })