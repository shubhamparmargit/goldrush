from django.shortcuts import render
from product.models import Metal, MetalPurity, MetalPurityPrice, MetalType, Unit, GenderCategories, Category, Product, Product_Images, Product_Videos, Stock, StockMovement
from utility.views import Utility, Validation, RandomIdGenerate, current_date, imageType_lst, urlPrefix, InvoiceUtil
from django.http.response import JsonResponse
from rest_framework import status
from django.db import transaction
from django.db import IntegrityError
import random, os
from django.conf import settings
from django.core.files.storage import default_storage, FileSystemStorage
from django.utils.datastructures import MultiValueDictKeyError
from PIL import Image
from django.utils import timezone

util_obj = Utility()
valid_obj = Validation()
random_obj = RandomIdGenerate()
invoice_util = InvoiceUtil()

class Pages:
    def metal_purity_price(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/metal-purity-price.html')
        else:
            return util_obj.goToLogin(request)

    def unit(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/unit.html')
        else:
            return util_obj.goToLogin(request)

    def category(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/category.html')
        else:
            return util_obj.goToLogin(request)

    def add_product(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/product.html')
        else:
            return util_obj.goToLogin(request)

    def product_list(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/product-list.html')
        else:
            return util_obj.goToLogin(request)
        
    def update_product(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    if request.GET.get('id') is not None:
                        prod_obj = ProductData()
                        data = prod_obj.getProduct(request.GET['id'])

                        if data.get('success') == '0':
                            return util_obj.printErrorResponse_200(data['message'])
                        
                        # print(data)
                        return render(request,'portal/update-product.html',{'data':data})
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def product_stock(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/product-stock.html')
        else:
            return util_obj.goToLogin(request)

    def set_product_session(self, request):
        if request.method == "POST":
            product_id = request.POST.get("product_id")
            request.session["product_id"] = product_id
            return JsonResponse({"success": True})
        return JsonResponse({"success": False})

    def stock_movement(self,request):
        if util_obj.checkSession(request) == False:
            # if request.method == 'GET':
                # try:
                    # if product is not None:
                    #     request.session['product_id'] = product
                    #     productObj = Product.objects.filter(unique_id__exact = product)
                        # return render(request,'portal/stock-movement.html',{'product_name':productObj[0].name})
                    # else:
                    #     return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
                # except:
                #     return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            # else:
            #     return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')

            product_id = request.session.get("product_id")
    
            if not product_id:
                return render(request, "portal/product-stock.html", {"message": "No product selected"})

            product = Product.objects.get(unique_id__exact=product_id)
            return render(request, "portal/stock-movement.html", {"product_name": product.name})
        else:
            return util_obj.goToLogin(request)
        
class MetalData:
    def getAllMetals(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    metals_list=Metal.objects.filter(access__exact = 'Granted')
                    data=[]
                    if len(metals_list)>0:
                        for row in metals_list:
                            data.append({'metal_id':row.unique_id, 'metal_name':row.metal_name})
                    return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

class MetalPurityData:
    def getPurityByMetal(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    metal_id = request.GET['metal_id']
                    if metal_id is not None and metal_id !="":
                        id_validate = valid_obj.validate_digit(metal_id=metal_id)
                        if id_validate != 1:
                            return util_obj.printErrorResponse_200(id_validate)

                        purity_list=MetalPurity.objects.filter(access__exact = 'Granted', metal_id = metal_id)
                        data=[]
                        if len(purity_list)>0:
                            for row in purity_list:
                                data.append({'purity_id':row.unique_id, 'purity_name':row.purity})
                        return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                    else:
                        return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')  
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
class MetalTypeData:
    def getTypeByMetal(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    metal_id = request.GET['metal_id']
                    if metal_id is not None and metal_id !="":
                        id_validate = valid_obj.validate_digit(metal_id=metal_id)
                        if id_validate != 1:
                            return util_obj.printErrorResponse_200(id_validate)

                        type_list=MetalType.objects.filter(access__exact = 'Granted', metal_id = metal_id)
                        data=[]
                        if len(type_list)>0:
                            for row in type_list:
                                data.append({'type_id':row.unique_id, 'type_name':row.type})
                        return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                    else:
                        return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')  
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

class PurityPrice:
    def addPurityPrice(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addMetalPurityPrice') is not None:
                        field=request.POST['field']
                        metal=request.POST['metal']
                        purity=request.POST['purity']
                        price=request.POST['price']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']

                        if field == "" and metal!="" and purity!="" and price!="":
                            digit_validate = valid_obj.validate_digit(metal=metal, purity=purity)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            amount_validate = valid_obj.validate_amount(price)
                            if amount_validate != 1:
                                return util_obj.printErrorResponse_200(amount_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)

                            with transaction.atomic():
                                unique_id = random_obj.generateUID()
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                insertData = MetalPurityPrice.objects.create(
                                    date = current_date,
                                    unique_id = unique_id,
                                    price_per_10_gm = price,
                                    access = access,
                                    metal = Metal.objects.get(unique_id=metal),
                                    purity = MetalPurity.objects.get(unique_id=purity),
                                )
                                if insertData:
                                    util_obj.activity_log(login_id,username,"Purity Price",f"Price Inserted Successfully => {purity}")

                                    return JsonResponse({'success':'1','message':'Price inseted successfully.'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('Price for this metal purity is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getPurityPrice(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('metal_purity_price') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            data = {}
                            priceObj = MetalPurityPrice.objects.select_related("metal","purity").all().filter(unique_id__exact=unique_id)

                            if len(priceObj) > 0:
                                for row in priceObj:
                                    date=timezone.localtime(row.date).strftime('%d-%m-%Y')
                                    formatted_price = util_obj.formatPrice(row.price_per_10_gm)
                                    data = {'success':'1', 'unique_id':row.unique_id, 'date':date, 'price':formatted_price, 'metal':row.metal.metal_name, 'metal_id':row.metal.unique_id, 'purity':row.purity.purity, 'purity_id':row.purity.unique_id, 'access':row.access}
                                return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
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
        
    def updatePurityPrice(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_editMetalPurityPrice') is not None:
                        field=request.POST['field']
                        unique_id=request.POST['price_id']
                        metal=request.POST['metal']
                        purity=request.POST['purity']
                        price=request.POST['price']
                        
                        if field == "" and unique_id!="" and metal!="" and purity!="" and price!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id, metal=metal, purity=purity)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            amount_validate = valid_obj.validate_amount(price)
                            if amount_validate != 1:
                                return util_obj.printErrorResponse_200(amount_validate)

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                priceObj = MetalPurityPrice.objects.filter(unique_id=unique_id)
                                if priceObj:
                                    affected_rows = priceObj.update(
                                        price_per_10_gm = price,
                                        metal = Metal.objects.get(unique_id=metal),
                                        purity = MetalPurity.objects.get(unique_id=purity),
                                    )
                                    if affected_rows>0:
                                        util_obj.activity_log(login_id,username,"Purity Price",f"Price Updated Successfully => {purity}")

                                        return JsonResponse({'success':'1','message':'Price updated successfully.'}, status=status.HTTP_200_OK)
                                    else:
                                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('Unable to find out details!')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('Price for this metal purity is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
    def getMetalPurityPrice(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('metal_purity_price') is not None:
                        metal_id=request.POST["metal_id"]
                        purity_id=request.POST["purity_id"]

                        if metal_id!="" and purity_id!="":
                            digit_validate = valid_obj.validate_digit(metal_id=metal_id,purity_id=purity_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            data = {}
                            priceObj = MetalPurityPrice.objects.all().filter(metal__unique_id__exact=metal_id, purity__unique_id__exact=purity_id)

                            if len(priceObj) > 0:
                                for row in priceObj:
                                    formatted_price = util_obj.formatPrice(row.price_per_10_gm)
                                    data = {'success':'1', 'price':formatted_price}
                                return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
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
        
class UnitData:
    def addUnit(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addUnit') is not None:
                        field=request.POST['field']
                        unit_name=request.POST['unit']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']

                        if field == "" and unit_name!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(unit_name=unit_name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)

                            with transaction.atomic():
                                unique_id = random_obj.generateUID()
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                insertData = Unit.objects.create(
                                    date = current_date,
                                    unique_id = unique_id,
                                    unit_name = unit_name,
                                    access = access,
                                )
                                if insertData:
                                    util_obj.activity_log(login_id,username,"Unit",f"Unit Inserted Successfully => {unique_id}")

                                    return JsonResponse({'success':'1','message':'Unit inseted successfully.'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('This unit is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getUnit(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('unit') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            data = {}
                            unitObj = Unit.objects.all().filter(unique_id__exact=unique_id)

                            if len(unitObj) > 0:
                                for row in unitObj:
                                    date=timezone.localtime(row.date).strftime('%d-%m-%Y')
                                    data = {'success':'1', 'unique_id':row.unique_id, 'date':date, 'unit_name':row.unit_name, 'access':row.access}
                                return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
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
        
    def updateUnit(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_editUnit') is not None:
                        field=request.POST['field']
                        unique_id=request.POST['unit_id']
                        unit_name=request.POST['unit']
                        
                        if field == "" and unique_id!="" and unit_name!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(unit_name=unit_name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                unitObj = Unit.objects.filter(unique_id=unique_id)
                                if unitObj:
                                    affected_rows = unitObj.update(
                                        unit_name = unit_name,
                                    )
                                    if affected_rows>0:
                                        util_obj.activity_log(login_id,username,"Unit",f"Unit Updated Successfully => {unique_id}")

                                        return JsonResponse({'success':'1','message':'Unit updated successfully.'}, status=status.HTTP_200_OK)
                                    else:
                                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('Unable to find out details!')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('This unit is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

class GenderData:
    def getAllGenders(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    gender_list=GenderCategories.objects.filter(access__exact = 'Granted')
                    data=[]
                    if len(gender_list)>0:
                        for row in gender_list:
                            data.append({'gender_id':row.unique_id, 'gender_name':row.gender_name})
                    return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
class CategoryData:
    imageWd = 200
    imageHg = 200
    def addCategory(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addCategory') is not None:
                        field=request.POST['field']
                        name=request.POST['name']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']

                        if field == "" and name!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(name=name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)

                            unique_id = random_obj.generateUID()
                            image_url=""
                            image_name=""
                            upload_dir = os.path.join(settings.MEDIA_ROOT,"category-images/"+str(unique_id)+"/")
                            image=request.FILES.get('image', False)
                            if image:
                                image_name='image_'+str(random.randint(100000,999999))+'.jpg'
                                image_url="category-images/"+str(unique_id)+"/"+image_name
                                
                                errors=valid_obj.validate_image(image,imageType_lst,'NA','NA')
                        
                                if(len(errors) > 0):
                                    return util_obj.printErrorResponse_200("Thumbnail :: "+", ".join(errors))
                            else:
                                return util_obj.printErrorResponse_200("Upload of image is mandatory!")

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                insertData = Category.objects.create(
                                    date = current_date,
                                    unique_id = unique_id,
                                    name = name,
                                    image = image_url,
                                    access = access,
                                )
                                if insertData:
                                    # Save image temporarily
                                    util_obj.create_media_folder("category-images/"+str(unique_id)+"/")
                                    temp_path = os.path.join(upload_dir, image_name)
                                    with default_storage.open(temp_path, 'wb+') as destination:
                                        for chunk in image.chunks():
                                            destination.write(chunk)

                                    # Resize image
                                    img = Image.open(temp_path)
                                    img = img.resize((self.imageWd, self.imageHg))
                                    img.save(temp_path)

                                    util_obj.activity_log(login_id,username,"Category",f"Category Inserted Successfully => {unique_id}")

                                    return JsonResponse({'success':'1','message':'Category inseted successfully.'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('This category is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getCategory(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('category') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            data = {}
                            catObj = Category.objects.all().filter(unique_id__exact=unique_id)

                            if len(catObj) > 0:
                                for row in catObj:
                                    date=timezone.localtime(row.date).strftime('%d-%m-%Y')
                                    data = {'success':'1', 'unique_id':row.unique_id, 'date':date, 'name':row.name, 'image':urlPrefix+row.image, 'access':row.access}
                                return JsonResponse(data, status=status.HTTP_200_OK,safe=False)  
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
        
    def updateCategory(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_editCategory') is not None:
                        field=request.POST['field']
                        unique_id=request.POST['category_id']
                        name=request.POST['name']
                        
                        if field == "" and unique_id!="" and name!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(name=name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                catObj = Category.objects.filter(unique_id=unique_id)
                                
                                image=request.FILES.get('image', False)
                                image_url=""
                                image_name=""
                                old_image_url = catObj[0].image
                                upload_dir = os.path.join(settings.MEDIA_ROOT,"category-images/"+str(unique_id)+"/")
                                image=request.FILES.get('image', False)
                                if image:
                                    image_name='image_'+str(random.randint(100000,999999))+'.jpg'
                                    image_url="category-images/"+str(unique_id)+"/"+image_name
                                    
                                    errors=valid_obj.validate_image(image,imageType_lst,'NA','NA')
                            
                                    if(len(errors) > 0):
                                        return util_obj.printErrorResponse_200("Thumbnail :: "+", ".join(errors))
                                else:
                                    image_url = old_image_url
                                
                                if catObj:
                                    affected_rows = catObj.update(
                                        name = name,
                                        image = image_url,
                                    )
                                    if affected_rows>0:
                                        if image:
                                            util_obj.create_media_folder("category-images/"+str(unique_id)+"/")
                                            temp_path = os.path.join(upload_dir, image_name)
                                            with default_storage.open(temp_path, 'wb+') as destination:
                                                for chunk in image.chunks():
                                                    destination.write(chunk)

                                            # Resize image
                                            img = Image.open(temp_path)
                                            img = img.resize((self.imageWd, self.imageHg))
                                            img.save(temp_path)

                                            if old_image_url!="" and os.path.exists("media/"+old_image_url):
                                                os.remove("media/"+old_image_url) 

                                        util_obj.activity_log(login_id,username,"Category",f"Category Updated Successfully => {unique_id}")

                                        return JsonResponse({'success':'1','message':'Category updated successfully.'}, status=status.HTTP_200_OK)
                                    else:
                                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('Unable to find out details!')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('This category is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getAllCategory(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    category_list=Category.objects.filter(access__exact = 'Granted')
                    data=[]
                    if len(category_list)>0:
                        for row in category_list:
                            data.append({'category_id':row.unique_id, 'category_name':row.name})
                    return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

class ProductData:
    def calculate_price(self, price_per_10_gm, weight, discount, making_charge, delivery_charge, gst):
        price_1_gm = float(price_per_10_gm)/10
        total = (price_1_gm*float(weight))
        discount_rs = 0
        if discount>0:
            discount_rs = total * (float(discount)/100)
        total_without_gst = (total + float(making_charge) + float(delivery_charge)) - discount_rs  
        gst_amount = total_without_gst * (float(gst) / 100)
        total_price = total_without_gst + gst_amount

        return (total, total_without_gst, total_price, gst_amount)

    def addProduct(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addProduct') is not None:
                        field=request.POST['field']
                        name=request.POST['name']
                        category=request.POST['category']
                        size=request.POST['size']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']
                        hot_sale='No'
                        if request.POST.get('hot_sale'):
                            hot_sale=request.POST['hot_sale']
                        description=request.POST['description']
                        category_description=request.POST['category_description']
                        metal=request.POST['metal']
                        metal_type=request.POST['metal_type']
                        purity=request.POST['purity']
                        price_per_10_gm=request.POST['price_per_10_gm']
                        weight=request.POST['weight']
                        gst=request.POST['gst']
                        making_fixed='No'
                        if request.POST.get('making_fixed'):
                            making_fixed=request.POST['making_fixed']
                        making_charge = float(request.POST.get('making_charge') or 0)
                        delivery_charge = float(request.POST.get('delivery_charge') or 0)
                        discount = float(request.POST.get('discount') or 0)

                        if field == "" and name!="" and category!="" and size!="" and metal!="" and metal_type!="" and purity!="" and price_per_10_gm!="" and weight!="" and gst!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(name=name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)
                            
                            digit_validate = valid_obj.validate_digit(category=category, metal=metal, metal_type=metal_type, purity=purity)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            amount_validate = valid_obj.validate_amount(price_per_10_gm)
                            if amount_validate != 1:
                                return util_obj.printErrorResponse_200(amount_validate)
                            
                            weight_validate = valid_obj.validate_floating_number(weight)
                            if weight_validate != 1:
                                return util_obj.printErrorResponse_200(weight_validate)
                            
                            gst_validate = valid_obj.validate_floating_number(gst)
                            if gst_validate != 1:
                                return util_obj.printErrorResponse_200(gst_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)
                            
                            yes_no_validate = valid_obj.validate_yesno(hot_sale=hot_sale, making_fixed=making_fixed)
                            if yes_no_validate != 1:
                                return util_obj.printErrorResponse_200(yes_no_validate)

                            with transaction.atomic():
                                unique_id = random_obj.generateUID()
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                calculatedPrice = self.calculate_price(price_per_10_gm, weight, discount, making_charge, delivery_charge, gst)
                                total_price = calculatedPrice[2]

                                insertData = Product.objects.create(
                                    date = current_date,
                                    unique_id = unique_id,
                                    name = name,
                                    category = Category.objects.get(unique_id=category),
                                    size = size,
                                    access = access, 
                                    hot_sale = hot_sale,
                                    description = bytes(description,'utf-8'),
                                    category_description = bytes(category_description,'utf-8'),
                                    metal = Metal.objects.get(unique_id=metal),
                                    metal_type = MetalType.objects.get(unique_id=metal_type),
                                    purity = MetalPurity.objects.get(unique_id=purity),
                                    price_per_10_gm = price_per_10_gm,
                                    weight_in_gm = weight,
                                    gst_in_percent = gst,
                                    making_fixed = making_fixed,
                                    making_charge = making_charge,
                                    delivery_charge = delivery_charge,
                                    discount_in_percent = discount,
                                    total_price = total_price,
                                )
                                if insertData:
                                    Stock.objects.create(
                                        product = Product.objects.get(unique_id = unique_id), 
                                        quantity = 0,
                                        last_updated = current_date,
                                        added_by = username
                                    )

                                    util_obj.activity_log(login_id,username,"Product",f"Product Inserted Successfully => {unique_id}")

                                    return JsonResponse({'success':'1','message':'Product inseted successfully.'}, status=status.HTTP_200_OK)
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('Product is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
    def getProduct(self, id):
        if not id:
            return {'success': '0', 'message': 'Something went wrong. Please try again later.'}

        unique_id = id

        digit_validate = valid_obj.validate_digit(unique_id=unique_id)
        if digit_validate != 1:
            return {'success': '0', 'message': str(digit_validate)}

        prod_image_list = self.getProductImages(unique_id)
        prod_video_list = self.getProductVideos(unique_id)

        row = Product.objects.filter(unique_id=unique_id).first()

        if not row:
            return {'success': '0', 'message': 'Data not found!'}

        # formatting
        frmt_price = str(invoice_util.money(row.price_per_10_gm))
        frmt_weight = str(invoice_util.money(row.weight_in_gm))
        frmt_gst = str(invoice_util.money(row.gst_in_percent))
        frmt_make_charge = str(invoice_util.money(row.making_charge))
        frmt_del_charge = str(invoice_util.money(row.delivery_charge))
        frmt_dis = str(invoice_util.money(row.discount_in_percent))
        frmt_total = str(invoice_util.money(row.total_price))

        return {
            'success': '1',
            'unique_id': row.unique_id,
            'name': row.name,
            'category': row.category.unique_id,
            'category_name': row.category.name,
            'size': row.size,
            'access': row.access,
            'hot_sale': row.hot_sale,
            'description': row.description.decode('utf-8'),
            'category_description': row.category_description.decode('utf-8'),
            'metal': row.metal.unique_id,
            'metal_name': row.metal.metal_name,
            'purity': row.purity.unique_id,
            'purity_name': row.purity.purity,
            'metal_type': row.metal_type.unique_id,
            'metal_type_name': row.metal_type.type,
            'price_per_10_gm': frmt_price,
            'weight_in_gm': frmt_weight,
            'gst_in_percent': frmt_gst,
            'making_fixed': row.making_fixed,
            'making_charge': frmt_make_charge,
            'delivery_charge': frmt_del_charge,
            'discount_in_percent': frmt_dis,
            'total_price': frmt_total,
            'access_states': "checked" if row.access == "Granted" else "",
            'sale_states': "checked" if row.hot_sale == "Yes" else "",
            'making_states': "checked" if row.making_fixed == "Yes" else "",
            'images': prod_image_list,
            'videos': prod_video_list
        }

    def getAllProduct(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'GET':
                try:
                    product_list=Product.objects.filter(access__exact = 'Granted')
                    data=[]
                    if len(product_list)>0:
                        for row in product_list:
                            data.append({'product_id':row.unique_id, 'product_name':row.name})
                    return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def getProductImages(self,unique_id):
        if unique_id is not None and unique_id!="":
            if unique_id!="":
                digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                if digit_validate != 1:
                    return {'success': '0', 'message': str(digit_validate)}

                data = []
                imageObj=Product_Images.objects.filter(product = unique_id).exclude(image_type='Thumbnail').order_by('-id')

                if len(imageObj) > 0:
                    for row in imageObj:
                        data.append({'image_id':row.unique_id, 'image_url':urlPrefix+row.image_url})
                #     return data  
                # else:
                #     return {'success': '0', 'message': 'Data not found!'}
                return data
            else:
                return {'success': '0', 'message': 'Please fill all the mandatory fields!'}
        else:
            return {'success': '0', 'message': 'Something went wrong. Please try again later.'}

    def getProductVideos(self,unique_id):
        if unique_id is not None and unique_id!="":
            if unique_id!="":
                digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                if digit_validate != 1:
                    return util_obj.printErrorResponse_200(digit_validate)

                data = []
                videoObj=Product_Videos.objects.filter(product = unique_id).order_by('-id')

                if len(videoObj) > 0:
                    for row in videoObj:
                        data.append({'video_id':row.unique_id, 'video_url':urlPrefix+row.video_url})
                #     return data  
                # else:
                #     return {'success': '0', 'message': 'Data not found!'}
                return data
            else:
                return {'success': '0', 'message': 'Please fill all the mandatory fields!'}
        else:
            return {'success': '0', 'message': 'Something went wrong. Please try again later.'}
        
    def updateProduct(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_updateProduct') is not None:
                        field=request.POST['field']
                        unique_id=request.POST['product_id']
                        name=request.POST['name']
                        category=request.POST['category']
                        size=request.POST['size']
                        access='Blocked'
                        if request.POST.get('access'):
                            access=request.POST['access']
                        hot_sale='No'
                        if request.POST.get('hot_sale'):
                            hot_sale=request.POST['hot_sale']
                        description=request.POST['description']
                        category_description=request.POST['category_description']
                        metal=request.POST['metal']
                        metal_type=request.POST['metal_type']
                        purity=request.POST['purity']
                        price_per_10_gm=request.POST['price_per_10_gm']
                        weight=request.POST['weight']
                        gst=request.POST['gst']
                        making_fixed='No'
                        if request.POST.get('making_fixed'):
                            making_fixed=request.POST['making_fixed']
                        making_charge = float(request.POST.get('making_charge') or 0)
                        delivery_charge = float(request.POST.get('delivery_charge') or 0)
                        discount = float(request.POST.get('discount') or 0)
                
                        if field == "" and name!="" and category!="" and size!="" and metal!="" and metal_type!="" and purity!="" and price_per_10_gm!="" and weight!="" and gst!="":
                            alpha_validate = valid_obj.validate_alpha_with_space(name=name)
                            if alpha_validate != 1:
                                return util_obj.printErrorResponse_200(alpha_validate)
                            
                            digit_validate = valid_obj.validate_digit(category=category, metal=metal, metal_type=metal_type, purity=purity)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            amount_validate = valid_obj.validate_amount(price_per_10_gm)
                            if amount_validate != 1:
                                return util_obj.printErrorResponse_200(amount_validate)
                            
                            weight_validate = valid_obj.validate_floating_number(weight)
                            if weight_validate != 1:
                                return util_obj.printErrorResponse_200(weight_validate)
                            
                            gst_validate = valid_obj.validate_floating_number(gst)
                            if gst_validate != 1:
                                return util_obj.printErrorResponse_200(gst_validate)

                            access_validate = valid_obj.validate_access(access)
                            if access_validate != 1:
                                return util_obj.printErrorResponse_200(access_validate)
                            
                            yes_no_validate = valid_obj.validate_yesno(hot_sale=hot_sale, making_fixed=making_fixed)
                            if yes_no_validate != 1:
                                return util_obj.printErrorResponse_200(yes_no_validate)

                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                calculatedPrice = self.calculate_price(price_per_10_gm, weight, discount, making_charge, delivery_charge, gst)
                                total_price = calculatedPrice[2]

                                prodObj = Product.objects.filter(unique_id=unique_id)
                                if prodObj:
                                    affected_rows = prodObj.update(
                                        name = name,
                                        category = Category.objects.get(unique_id=category),
                                        size = size,
                                        access = access, 
                                        hot_sale = hot_sale,
                                        description = bytes(description,'utf-8'),
                                        category_description = bytes(category_description,'utf-8'),
                                        metal = Metal.objects.get(unique_id=metal),
                                        metal_type = MetalType.objects.get(unique_id=metal_type),
                                        purity = MetalPurity.objects.get(unique_id=purity),
                                        price_per_10_gm = price_per_10_gm,
                                        weight_in_gm = weight,
                                        gst_in_percent = gst,
                                        making_fixed = making_fixed,
                                        making_charge = making_charge,
                                        delivery_charge = delivery_charge,
                                        discount_in_percent = discount,
                                        total_price = total_price,
                                    )
                                    if affected_rows>0:
                                        util_obj.activity_log(login_id,username,"Product",f"Product Updated Successfully => {unique_id}")

                                        return JsonResponse({'success':'1','message':'Product updated successfully.'}, status=status.HTTP_200_OK)
                                    else:
                                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('Unable to find out details!')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('Price for this metal purity is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def showProductImages(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('showProductImages') is not None:
                        unique_id=request.POST["product_id"]

                        if unique_id!="":
                            data = self.getProductImages(unique_id)
                            if data.get('success') == '0':
                                return util_obj.printErrorResponse_200(data['message'])
                            return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
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

    def showVideos(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('showVideos') is not None:
                        unique_id=request.POST["product_id"]

                        if unique_id!="":
                            data = self.getProductVideos(unique_id)
                            if data.get('success') == '0':
                                return util_obj.printErrorResponse_200(data['message'])
                            return JsonResponse(data, status=status.HTTP_200_OK,safe=False)
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

    def uploadProductImages(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.GET.get('product_id') is not None:
                        unique_id=request.GET["product_id"]
                        image_type = ''

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            username = request.session['logged']
                            files = request.FILES.getlist('file')
                            util_obj.create_media_folder("product/"+str(unique_id)+"/images/")
                            
                            if files:
                                for file_ in files:
                                    file_url=""
                                    fss=""
                                    filename=""
                                    img_unique_id = random_obj.generateUID()
                                    
                                    try:
                                        prod_img = file_
                                        fss = FileSystemStorage(os.path.join(settings.MEDIA_ROOT,"product/"+str(unique_id)+"/images/"))
                                        filename=prod_img.name
                                        file_url = "product/"+str(unique_id)+"/images/"+filename
                                    except MultiValueDictKeyError:
                                        pass
                                    
                                    if (file_url) is not None:
                                        try:
                                            insertData = Product_Images.objects.create(
                                                unique_id = img_unique_id,
                                                image_url = file_url,
                                                product = Product.objects.get(unique_id=unique_id),
                                                date = current_date,
                                                added_by = username,
                                                image_type = image_type
                                            )
                                            if insertData:
                                                #save file after data stored
                                                try:
                                                    fss.save(filename, prod_img)
                                                except MultiValueDictKeyError:
                                                    pass
                                        except IntegrityError:
                                            pass
                                    return JsonResponse({'success':'1','message':'Product images updated successfully...',"image_id":Product_Images.objects.last().unique_id,"image_url":Product_Images.objects.last().image_url}, status=status.HTTP_200_OK)
                                  
                            else:
                                return util_obj.printErrorResponse_200('file not found!')
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
    
    def uploadVideos(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.GET.get('product_id') is not None:
                        unique_id=request.GET["product_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            username = request.session['logged']
                            files = request.FILES.getlist('file')
                            util_obj.create_media_folder("product/"+str(unique_id)+"/videos/")
                            
                            if files:
                                for file_ in files:
                                    file_url=""
                                    fss=""
                                    filename=""
                                    vid_unique_id = random_obj.generateUID()

                                    try:
                                        prod_img = file_
                                        fss = FileSystemStorage(os.path.join(settings.MEDIA_ROOT,"product/"+str(unique_id)+"/videos/"))
                                        filename=prod_img.name
                                        file_url = "product/"+str(unique_id)+"/videos/"+filename
                                    except MultiValueDictKeyError:
                                        pass
                                    
                                    if (file_url) is not None:
                                        try:
                                            insertData = Product_Videos.objects.create(
                                                unique_id = vid_unique_id,
                                                video_url = file_url,
                                                product = Product.objects.get(unique_id=unique_id),
                                                date = current_date,
                                                added_by = username
                                            )
                                            if insertData:
                                                #save file after data stored
                                                try:
                                                    fss.save(filename, prod_img)
                                                except MultiValueDictKeyError:
                                                    pass
                                        except IntegrityError:
                                            pass
                                    return JsonResponse({'success':'1','message':'Product videos updated successfully...',"video_id":Product_Videos.objects.last().unique_id,"video_url":Product_Videos.objects.last().video_url}, status=status.HTTP_200_OK)
                                  
                            else:
                                return util_obj.printErrorResponse_200('file not found!')
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
        
    def deleteProductImage(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('deleteProductImage') is not None:
                        unique_id=request.POST["image_id"]
                        image_url=request.POST['image_url']

                        if unique_id!="" and image_url!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            imgeObj=Product_Images.objects.get(unique_id = unique_id)

                            if imgeObj:
                                if imgeObj.delete():
                                    if os.path.exists("media/"+image_url):
                                        os.remove("media/"+image_url) 
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
        
    def deleteVideo(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('deleteVideo') is not None:
                        unique_id=request.POST["video_id"]
                        video_url=request.POST['video_url']

                        if unique_id!="" and video_url!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            videoObj=Product_Videos.objects.get(unique_id = unique_id)

                            if videoObj:
                                if videoObj.delete():
                                    if os.path.exists("media/"+video_url):
                                        os.remove("media/"+video_url) 
                                    return JsonResponse({'success':'1','message': 'Video deleted successfully...'}, status=status.HTTP_200_OK)
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

class StockOperation:
    def addStock(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_addStock') is not None:
                        field=request.POST['field']
                        product=request.POST['product']
                        quantity=request.POST['quantity']
                        reference=request.POST['reference']
                        
                        if field == "" and product!="" and quantity!="":
                            digit_validate = valid_obj.validate_digit(product=product, quantity=quantity)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                        
                            with transaction.atomic():
                                login_id = request.session['login_id']
                                username = request.session['logged']

                                stock = Stock.objects.filter(product__unique_id = product)
                                if stock:
                                    qny = stock[0].quantity
                                    StockMovement.objects.create(
                                        product = Product.objects.get(unique_id = product), 
                                        movement_type = "IN", 
                                        quantity = quantity, 
                                        reference = reference,
                                        movement_date = current_date,
                                        added_by = username
                                    )

                                    affected_rows = stock.update(
                                        quantity = int(quantity) + qny,
                                        last_updated = current_date
                                    )

                                    if affected_rows>0:
                                        util_obj.activity_log(login_id,username,"Product Stock",f"Product Stock Inserted Successfully => {quantity}")

                                        return JsonResponse({'success':'1','message':'Product stock inseted successfully.'}, status=status.HTTP_200_OK)
                                    else:
                                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                        else:
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except IntegrityError as ie:
                    return util_obj.printErrorResponse_200('Product is already present. Kindly add another') 
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)