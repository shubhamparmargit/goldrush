from django.shortcuts import render
from utility.views import Utility, Validation, RandomIdGenerate, imageType_lst, current_date
import os, random, datetime
from django.conf import settings
from django.db import transaction
from django.core.files.storage import default_storage
from PIL import Image
from django.http.response import JsonResponse
from rest_framework import status
from django.utils import timezone
from portal_misc.models import ImageSlider, BankHoliday

util_obj = Utility()
valid_obj = Validation()
random_obj = RandomIdGenerate()

class Pages:
    def image_slider(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/image-slider.html')
        else:
            return util_obj.goToLogin(request)

    def contact_messages(self,request):
        return render(request, 'portal/contact-messages.html')

    def bank_holidays(self, request):
        if util_obj.checkSession(request) == False:
            return render(request, 'portal/bank-holidays.html', {
                'today': datetime.date.today().isoformat()
            })
        else:
            return util_obj.goToLogin(request)

class ImageData:
    def addImage(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addImageSlider') is not None:
                        type_arr=["Slider","Banner"]
                        field=request.POST['field']
                        image_type=request.POST['image_type']
                        sequence=request.POST['sequence']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']

                        if field == "" and image_type!="" and sequence !="":
                            if image_type not in type_arr:
                                return util_obj.printErrorResponse_200("Image type is not valid")

                            digit_validate = valid_obj.validate_digit(sequence = sequence)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)

                            unique_id = random_obj.generateUID()
                            image_url=""
                            image_name=""
                            upload_dir = os.path.join(settings.MEDIA_ROOT,"image_slider/")
                            image=request.FILES.get('image', False)
                            if image:
                                file_name, file_extension = os.path.splitext(image.name)
                                image_name='Photo_'+image_type+'_'+str(random.randint(100000,999999))+file_extension
                                image_url="image_slider/"+image_name

                                errors=valid_obj.validate_image(image,imageType_lst,'NA','NA')

                                if(len(errors) > 0):
                                    return util_obj.printErrorResponse_200(", ".join(errors))
                            else:
                                return util_obj.printErrorResponse_200("Upload of image is mandatory!")

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                insertData = ImageSlider.objects.create(
                                    date = current_date,
                                    unique_id = unique_id,
                                    image_type = image_type,
                                    sequence = sequence,
                                    image = image_url,
                                    access = access,
                                    added_by = username
                                )
                                if insertData:
                                    util_obj.create_media_folder("image_slider/")
                                    temp_path = os.path.join(upload_dir, image_name)
                                    with default_storage.open(temp_path, 'wb+') as destination:
                                        for chunk in image.chunks():
                                            destination.write(chunk)

                                    img = Image.open(temp_path)
                                    img.save(temp_path)

                                    util_obj.activity_log(login_id,username,"Image",f"Image Inserted Successfully => {unique_id}")

                                    return JsonResponse({'success':'1','message':'Image inseted successfully.'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def deleteImage(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('image_slider') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            login_id = request.session['login_id']
                            username = request.session['logged']
                            imgeObj = ImageSlider.objects.get(unique_id = unique_id)

                            if imgeObj:
                                if imgeObj.delete():
                                    if os.path.exists("media/"+imgeObj.image):
                                        os.remove("media/"+imgeObj.image)

                                    util_obj.activity_log(login_id,username,"Image",f"Image Deleted Successfully => {unique_id}")

                                    return JsonResponse({'success':'1','message': 'Image deleted successfully...'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                            else:
                                return util_obj.printErrorResponse_200('Data not found!')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)


class BankHolidayData:

    def list_holidays(self, request):
        if util_obj.checkSession(request) != False:
            return util_obj.goToLogin(request)
        try:
            holidays = BankHoliday.objects.all().order_by('date')
            data = []
            for h in holidays:
                data.append({
                    'id': h.id,
                    'date': h.date.strftime('%d-%m-%Y'),
                    'date_raw': str(h.date),
                    'description': h.description,
                    'is_active': h.is_active,
                    'added_by': h.added_by,
                    'added_on': timezone.localtime(h.added_on).strftime('%d-%m-%Y %I:%M %p'),
                })
            return JsonResponse({'success': '1', 'data': data})
        except Exception:
            return JsonResponse({'success': '0', 'message': 'Something went wrong'})

    def add_holiday(self, request):
        if util_obj.checkSession(request) != False:
            return util_obj.goToLogin(request)
        if request.method != 'POST':
            return JsonResponse({'success': '0', 'message': 'Invalid request'})
        try:
            date_str = request.POST.get('date', '').strip()
            description = request.POST.get('description', '').strip()
            username = request.session.get('logged', 'admin')

            if not date_str or not description:
                return JsonResponse({'success': '0', 'message': 'Date and description are required'})

            try:
                holiday_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': '0', 'message': 'Invalid date format'})

            if BankHoliday.objects.filter(date=holiday_date).exists():
                return JsonResponse({'success': '0', 'message': 'Holiday already exists for this date'})

            BankHoliday.objects.create(
                date=holiday_date,
                description=description,
                added_by=username,
            )
            return JsonResponse({'success': '1', 'message': 'Bank holiday added successfully'})
        except Exception:
            return JsonResponse({'success': '0', 'message': 'Something went wrong'})

    def delete_holiday(self, request):
        if util_obj.checkSession(request) != False:
            return util_obj.goToLogin(request)
        if request.method != 'POST':
            return JsonResponse({'success': '0', 'message': 'Invalid request'})
        try:
            holiday_id = request.POST.get('id', '').strip()
            if not holiday_id:
                return JsonResponse({'success': '0', 'message': 'Invalid holiday ID'})
            obj = BankHoliday.objects.get(id=holiday_id)
            obj.delete()
            return JsonResponse({'success': '1', 'message': 'Bank holiday deleted successfully'})
        except BankHoliday.DoesNotExist:
            return JsonResponse({'success': '0', 'message': 'Holiday not found'})
        except Exception:
            return JsonResponse({'success': '0', 'message': 'Something went wrong'})

    def toggle_holiday(self, request):
        if util_obj.checkSession(request) != False:
            return util_obj.goToLogin(request)
        if request.method != 'POST':
            return JsonResponse({'success': '0', 'message': 'Invalid request'})
        try:
            holiday_id = request.POST.get('id', '').strip()
            if not holiday_id:
                return JsonResponse({'success': '0', 'message': 'Invalid holiday ID'})
            obj = BankHoliday.objects.get(id=holiday_id)
            obj.is_active = not obj.is_active
            obj.save(update_fields=['is_active'])
            status_text = 'activated' if obj.is_active else 'deactivated'
            return JsonResponse({'success': '1', 'message': f'Holiday {status_text} successfully', 'is_active': obj.is_active})
        except BankHoliday.DoesNotExist:
            return JsonResponse({'success': '0', 'message': 'Holiday not found'})
        except Exception:
            return JsonResponse({'success': '0', 'message': 'Something went wrong'})
