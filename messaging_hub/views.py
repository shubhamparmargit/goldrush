from django.shortcuts import render
from rest_framework import status
from django.http.response import JsonResponse
from firebase_admin import messaging
import json
from django.views.decorators.csrf import csrf_exempt

from email.mime.multipart import MIMEMultipart
from django.conf import settings
from email.mime.text import MIMEText
import smtplib,ssl
from messaging_hub.email_templates import EmailTemplates
from email import encoders
from django.core.mail import send_mail

class FCMNotification:
    @csrf_exempt
    def send_notification_to_single_device(self, request):
        try:
            data = json.loads(request.body)
            token = data.get("fcm_token")  # Flutter device FCM token
            title = data.get("title", "New Notification")
            body = data.get("body", "You have a new message!")

            message = messaging.Message(
                notification=messaging.Notification(title=title, body=body),
                token=token
            )

            response = messaging.send(message)
            return JsonResponse({"message": "Notification sent", "response": response})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

email_obj = EmailTemplates()

class MailNotification:
    def sendMail(self, data):
        # print("Sending email to:", data)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = data["subject"]
        msg["From"] = settings.DEFAULT_FROM_EMAIL
        msg["To"] = data["to_email"]
        msg["Cc"] = data.get("cc_email", "")  # Prevents NoneType error
        msg["Bcc"] = data.get("bcc_email", "")  # Prevents NoneType error

        # HTML Message Part
        html = data["msg"]
        part = MIMEText(html, "html")
        # encoders.encode_base64(part)
        msg.attach(part)

        # Recipients List
        recipients = [msg["To"]]
        if msg["Cc"]:
            recipients.append(msg["Cc"])
        if msg["Bcc"]:
            recipients.append(msg["Bcc"])

        # try:
        #     with smtplib.SMTP_SSL("localhost") as server:
        #         server.sendmail(
        #             msg["From"], recipients, msg.as_string()
        #         )
        #         server.quit()
        #         return JsonResponse({"message": "Email sent successfully via localhost!"})
        # except Exception as e:
        #     return JsonResponse({"message": "Error sending email:"+e})

        # gmail
        try:
            # Connect to Gmail's SMTP server using port 587 and STARTTLS
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()  # Optional: identify ourselves to the server
                server.starttls()  # Upgrade the connection to secure TLS
                server.ehlo()  # Optional: re-identify as an encrypted connection
                server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                server.sendmail(msg["From"], recipients, msg.as_string())
            # return JsonResponse({"message": "Email sent successfully via Gmail!"})
            return 1
        except Exception as e:
            # return JsonResponse({"message": "Error sending email: " + str(e)})
            return 0

    # @csrf_exempt
    # def testMail(self, request):
    #     data = email_obj.welcome_message('Shalini Singh', 'shalini7548@gmail.com', '8082019432', 'shalini')
    #     return self.sendMail(data)

    # @csrf_exempt
    # def send_test_email(self, request):
    #     subject = 'Test Email via Sendmail Backend'
    #     message = 'This email is sent using Django sendmail backend.'
    #     recipient_list = ['shalini7548@gmail.com']
        
    #     send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, recipient_list)

    #     return JsonResponse({"message": "Email sent successfully via localhost!"})

    def welcomeMessage(self, name, email, mobile, password):
        data = email_obj.welcome_message(name, email, mobile, password)
        return self.sendMail(data)
    
    def passwordReset(self, name, email, username, unique_id, page_name, domain):
        data = email_obj.password_reset_template(name, email, username, unique_id, page_name, domain)
        return self.sendMail(data)
    
    def send_otp(self, name, email, otp):
        data = email_obj.otp_template(name, email, otp)
        return self.sendMail(data)