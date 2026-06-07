from django.shortcuts import render
from utility.views import Utility, Encryption, PasswordUtility
from customer.models import PasswordResetRequest, Customer
from django.http.response import JsonResponse
from django.db import transaction
from django.utils import timezone
from messaging_hub.views import MailNotification

mail_obj = MailNotification()
util_obj = Utility()
encrypt_obj = Encryption()
pass_obj = PasswordUtility()

class Pages:
    def validate_cust_reset_link(self, request):
        unique_id = request.GET.get('id')
        model_class = PasswordResetRequest
        context = pass_obj.generic_reset_link_validation(model_class, unique_id)
        return render(request, 'portal/set-customer-password.html', {'context': context})
            
class PasswordReset:
    def set_new_customer_password(self,request):
        if request.method == "POST":
            unique_id = request.POST.get('unique_id')
            password = request.POST.get('password') 
            confirm_password = request.POST.get('confirm_password')

            # 1. Mandatory Fields Check
            if not password or not confirm_password or password != confirm_password:
                return JsonResponse({'success': 0, 'message': 'Passwords do not match or fields are empty!', 'btn':False})

            try:
                reset_obj = PasswordResetRequest.objects.get(unique_id=unique_id)
                
                if reset_obj.password_changed == "Yes" or timezone.now() > reset_obj.valid_till or reset_obj.link_status=='Expired':
                    return JsonResponse({'success': 0, 'message': 'The URL you tried to use is either incorrect or no longer valid.', 'btn':False})

                # try:
                user = Customer.objects.get(email=reset_obj.email, unique_id=reset_obj.customer.unique_id, access='Granted')
                
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

                return JsonResponse({'success': 1, 'message': 'Password Updated.', 'btn':False})

                # except Customer.DoesNotExist:
                    # return JsonResponse({'success': 0, 'message': 'User not found or access denied.', 'btn':False})

            except PasswordResetRequest.DoesNotExist:
                return JsonResponse({'success': 0, 'message': 'The URL you tried to use is either incorrect or no longer valid.', 'btn':False})

        return JsonResponse({'success': 0, 'message': 'Invalid request method.', 'btn':False})