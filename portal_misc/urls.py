from portal_misc.views import *
from django.urls import include, re_path, path

page_obj = Pages()
image_obj = ImageData()
holiday_obj = BankHolidayData()

urlpatterns = [
   re_path(r'^image_slider$', page_obj.image_slider, name='image_slider'),
   re_path(r'^contact-messages$', page_obj.contact_messages, name='contact_messages'),

   re_path(r'^add-image$', image_obj.addImage, name='addImage'),
   re_path(r'^delete-image$', image_obj.deleteImage, name='deleteImage'),

   re_path(r'^bank-holidays$', page_obj.bank_holidays, name='bank_holidays'),
   re_path(r'^bank-holidays/list$', holiday_obj.list_holidays, name='list_holidays'),
   re_path(r'^bank-holidays/add$', holiday_obj.add_holiday, name='add_holiday'),
   re_path(r'^bank-holidays/delete$', holiday_obj.delete_holiday, name='delete_holiday'),
   re_path(r'^bank-holidays/toggle$', holiday_obj.toggle_holiday, name='toggle_holiday'),
]