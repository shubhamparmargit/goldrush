from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utility.views import Utility, urlPrefix, InvoiceUtil
from django.core.exceptions import ValidationError
from django.conf import settings
from product.models import Category, Product, Product_Images
from product.views import ProductData
from django.db.models import Q

util_obj = Utility()
invoice_util = InvoiceUtil()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def categories(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                catObj = Category.objects.filter(access = 'Granted')
                if catObj:
                    data = []
                    for row in catObj:
                        data.append({'unique_id':row.unique_id, 'name':row.name, 'image':urlPrefix+row.image, 'access':row.access})
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def products(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            category_id = request.POST.get('category_id','')
            hot_sale = request.POST.get('hot_sale','')
            searchTerm = request.POST.get('searchTerm','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                query = Product.objects.select_related("category","metal","metal_type","purity").all()

                conditions={}

                conditions['access__exact'] = 'Granted'

                if searchTerm != '':
                    search_tearm = searchTerm
                    query=query.filter(Q(total_price__icontains=search_tearm) | Q(metal__metal_name__icontains=search_tearm) | Q(purity__purity__icontains=search_tearm) | Q(metal_type__type__icontains=search_tearm) | Q(category__name__icontains=search_tearm) | Q(name__icontains=search_tearm) | Q(size__icontains=search_tearm) | Q(hot_sale__icontains=search_tearm))

                if hot_sale != '':
                    conditions['hot_sale__exact'] = hot_sale

                if category_id != '':
                    conditions['category__unique_id__exact'] = category_id
                
                if(len(conditions)>0):
                    query=query.filter(**conditions)
                    
                query=query.order_by('-id')

                total_data = len(query)

                data = []
                
                if total_data > 0:
                    for row in query:
                        product_image = ''
                        imageObj = Product_Images.objects.filter(product = row.unique_id)[0]
                        if imageObj:
                            product_image = urlPrefix+imageObj.image_url
                        formatted_price = str(invoice_util.money(row.total_price))
                        data.append({'unique_id':row.unique_id, 'price':formatted_price, 'metal':row.metal.metal_name, 'purity':row.purity.purity, 'metal_type':row.metal_type.type, 'category':row.category.name, 'category_id':row.category.unique_id, 'name':row.name, 'size':row.size, 'hot_sale':row.hot_sale,'image':product_image})
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def product_detail(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            product_id = request.POST.get('product_id','')
            
            if field == "" and mobile != "" and user_unique_id != "" and product_id != "":
                obj = ProductData()
                data = obj.getProduct(product_id)
                if data:
                    return Response(data, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  