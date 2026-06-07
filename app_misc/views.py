from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utility.views import Validation, urlPrefix, domainURL
from django.core.exceptions import ValidationError
from app_misc.models import AppVersion
from portal_misc.models import ImageSlider
from django.db import connection

valid_obj = Validation()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def checkAppVersion(request):
    if request.method == 'POST':
        try:
            field = request.POST['field']
            app_version = request.POST.get('app_version','')
            
            if field == "" and app_version != "":
                appObj = AppVersion.objects.filter(version_number = app_version)
                if appObj:
                    return Response({'success':'1','app_version':appObj[0].version_number}, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  
        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def imageSlider(request):
    if request.method == 'GET':
        try:
            sliderList = []
            bannerList = []

            sliderObj = ImageSlider.objects.filter(image_type = 'Slider', access = 'Granted').order_by('sequence')
            if sliderObj:
                for row in sliderObj:
                    sliderList.append({'image':urlPrefix+row.image})

            bannerObj = ImageSlider.objects.filter(image_type = 'Banner', access = 'Granted').order_by('sequence')
            if bannerObj:
                for row in bannerObj:
                    bannerList.append({'image':urlPrefix+row.image})
                
            return Response({'slider':sliderList,'banner':bannerList}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def options(request):
    if request.method == 'GET':
        try:
            linkList = []

            linkList.append({'page':'terms_and_conditions','url':domainURL+'ecomm-terms-condition'})
            linkList.append({'page':'privacy_policy','url':domainURL+'ecomm-privacy-policy'})
            linkList.append({'page':'refund_policy','url':domainURL+'refund-policy'})
            linkList.append({'page':'faq','url':domainURL+'index#faq'})
            
            return Response({'links':linkList}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  

@api_view(['GET'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def getPincodeDetails(request, pincode):
    try:

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT
                    office_name,
                    office_type,
                    delivery,
                    circle_name,
                    district,
                    division_name,
                    region_name,
                    state_name,
                    pincode
                FROM pincode_master
                WHERE pincode = %s
                ORDER BY office_name
            """, [pincode])

            rows = cursor.fetchall()

        if not rows:

            return Response([
                {
                    "Message": "No records found",
                    "Status": "Error",
                    "PostOffice": None
                }
            ], status=status.HTTP_200_OK)

        postOfficeList = []

        for row in rows:

            postOfficeList.append({
                "Name": row[0],
                "Description": None,
                "BranchType": row[1],
                "DeliveryStatus": row[2],
                "Circle": row[3],
                "District": row[4],
                "Division": row[5],
                "Region": row[4],
                "Block": row[4],  # agar Block column nahi hai to District use kar lo
                "State": row[7],
                "Country": "India",
                "Pincode": str(row[8])
            })

        response_data = [
            {
                "Message": f"Number of pincode(s) found:{len(postOfficeList)}",
                "Status": "Success",
                "PostOffice": postOfficeList
            }
        ]

        return Response(
            response_data,
            status=status.HTTP_200_OK
        )

    except Exception as e:

        return Response([
            {
                "Message": str(e),
                "Status": "Error",
                "PostOffice": None
            }
        ], status=status.HTTP_200_OK)