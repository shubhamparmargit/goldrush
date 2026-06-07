from messaging_hub.views import *
from django.urls import include, re_path, path

fcm_obj = FCMNotification()
mail_obj = MailNotification()

urlpatterns = [
    re_path(r'^send-fcm-single-device$', fcm_obj.send_notification_to_single_device, name="send_notification_to_single_device"),
    
    # re_path(r'^test-mail$', mail_obj.testMail, name="testMail"),
    # re_path(r'^send-mail$', mail_obj.send_test_email, name="send_test_email"),

]