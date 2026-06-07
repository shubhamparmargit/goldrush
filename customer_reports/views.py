from django.shortcuts import render
from utility.views import Utility, Validation, RandomIdGenerate, current_date, InvoiceUtil, urlPrefix
from django.conf import settings
from django.db import transaction
from django.http.response import JsonResponse
from rest_framework import status
from customer.models import Customer, MacResetDetails, CustomerAddress
from customer.views import CustomerData
from customer_wallet.models import WalletRechargeHistory
from django.utils import timezone
from datetime import timedelta
import os
from customer_order.models import Order, OrderDetails, OrderStatus, Cart
from customer_order.views import CustomerOrderData, CustomerCartData
from django.template.loader import get_template
from io import BytesIO
from xhtml2pdf import pisa
from django.http import HttpResponse

util_obj = Utility()
valid_obj = Validation()
random_obj = RandomIdGenerate()
cust_obj = CustomerData()
cust_odr_obj = CustomerOrderData() 
cust_cart_obj = CustomerCartData()
invoice_util = InvoiceUtil()

class Pages:
    def customer_list(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/customer-list.html')
        else:
            return util_obj.goToLogin(request)
        
    def customer_cart_list(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/customer-cart-list.html')
        else:
            return util_obj.goToLogin(request)
        
    def customer_order_list(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/customer-order-list.html')
        else:
            return util_obj.goToLogin(request)

    def registration_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/registration-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def transaction_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/transaction-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def wallet_recharge_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/wallet-recharge-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def first_recharge_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/first-recharge-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def customer_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/customer-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def customer_transfer_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/customer-transfer-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def order_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/order-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def no_recharge_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/no-recharge-report.html')
        else:
            return util_obj.goToLogin(request)
        
    def inactive_customer_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/inactive-customer-report.html')
        else:
            return util_obj.goToLogin(request)

    def withdrawal_report(self,request):
        if util_obj.checkSession(request) == False:
            return render(request,'portal/withdrawal-report.html')
        else:
            return util_obj.goToLogin(request)

class CustomerOperation:
    def macReset(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('mac_reset') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)
                            
                            u_id = random_obj.generateUID()
                            login_id = request.session['login_id']
                            username = request.session['logged']
                            custObj = Customer.objects.filter(unique_id = unique_id)
                            if custObj:
                                if custObj[0].unique_application_id != "":
                                    mac_reset_count = custObj[0].mac_reset_count + 1
                                    with transaction.atomic():
                                        insertData = MacResetDetails.objects.create(
                                            date = current_date,
                                            unique_id = u_id,
                                            old_unique_application_id = custObj[0].unique_application_id,
                                            old_app_id_date = custObj[0].app_id_date,
                                            device_details = custObj[0].device_details,
                                            customer = Customer.objects.get(unique_id=unique_id),
                                            added_by = username,
                                        )
                                        if insertData:
                                            affected_rows = custObj.update(
                                            unique_application_id = '',
                                            app_id_date = None,
                                            device_details = None,
                                            mac_reset_count = mac_reset_count
                                            )

                                            if affected_rows>0:
                                                util_obj.activity_log(login_id,username,"Mac Reset",f"Mac Reset Done Successfully => {unique_id}")

                                                return JsonResponse({'success':'1','message':'Mac Reset Done Successfully'}, status=status.HTTP_200_OK) 
                                            else:
                                                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                        else:
                                            return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                                else:
                                    return util_obj.printErrorResponse_200('No data for resetting...')    
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
        
    def getCustomer(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('customer') is not None:
                        unique_id=request.POST["unique_id"]

                        if unique_id!="":
                            digit_validate = valid_obj.validate_digit(unique_id=unique_id)
                            if digit_validate != 1:
                                return util_obj.printErrorResponse_200(digit_validate)

                            login_success = Customer.objects.filter(unique_id = unique_id)[0]

                            if login_success:
                                data = cust_obj.getCustomer(login_success)
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

    def getCustomerForEdit(self, request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    unique_id = request.POST.get('unique_id', '').strip()
                    if not unique_id:
                        return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')

                    customer = Customer.objects.filter(unique_id=unique_id).first()
                    if not customer:
                        return util_obj.printErrorResponse_200('Customer not found!')

                    addresses = []
                    for addr in CustomerAddress.objects.filter(customer=customer, access='Granted'):
                        addresses.append({
                            'unique_id': addr.unique_id,
                            'name': addr.name,
                            'mobile': addr.mobile,
                            'pincode': addr.pincode,
                            'postoffice': addr.postoffice,
                            'state': addr.state,
                            'city': addr.city,
                            'district': addr.district,
                            'region': addr.region,
                            'address_line_1': addr.address_line_1,
                            'address_line_2': addr.address_line_2,
                        })

                    data = {
                        'success': '1',
                        'unique_id': customer.unique_id,
                        'name': customer.name,
                        'mobile': customer.mobile,
                        'email': customer.email,
                        'aadhaar_number': customer.aadhaar_number,
                        'aadhaar_front_image': urlPrefix + customer.aadhaar_front_image if customer.aadhaar_front_image else '',
                        'aadhaar_back_image': urlPrefix + customer.aadhaar_back_image if customer.aadhaar_back_image else '',
                        'pan_number': customer.pan_number,
                        'pan_front_image': urlPrefix + customer.pan_front_image if customer.pan_front_image else '',
                        'referral_code': customer.referral_code,
                        'access': customer.access,
                        'trading': customer.trading,
                        'addresses': addresses,
                    }
                    return JsonResponse(data, status=status.HTTP_200_OK)
                except Exception as e:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

    def updateCustomer(self, request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    unique_id   = request.POST.get('unique_id', '').strip()
                    name        = request.POST.get('name', '').strip()
                    mobile      = request.POST.get('mobile', '').strip()
                    email       = request.POST.get('email', '').strip()
                    aadhaar_num = request.POST.get('aadhaar_number', '').strip()
                    pan_num     = request.POST.get('pan_number', '').strip()
                    referral    = request.POST.get('referral_code', '').strip()
                    access      = request.POST.get('access', '').strip()
                    trading     = request.POST.get('trading', '').strip()

                    if not unique_id:
                        return JsonResponse({'success': '0', 'message': 'Invalid request'})

                    if access not in ('Granted', 'Blocked'):
                        return JsonResponse({'success': '0', 'message': 'Invalid access value'})
                    if trading not in ('ON', 'OFF'):
                        return JsonResponse({'success': '0', 'message': 'Invalid trading value'})

                    customer = Customer.objects.filter(unique_id=unique_id).first()
                    if not customer:
                        return JsonResponse({'success': '0', 'message': 'Customer not found'})

                    # duplicate mobile/email check (exclude current customer)
                    if Customer.objects.filter(mobile=mobile).exclude(unique_id=unique_id).exists():
                        return JsonResponse({'success': '0', 'message': 'Mobile number already registered'})
                    if Customer.objects.filter(email=email).exclude(unique_id=unique_id).exists():
                        return JsonResponse({'success': '0', 'message': 'Email already registered'})
                    if Customer.objects.filter(aadhaar_number=aadhaar_num).exclude(unique_id=unique_id).exists():
                        return JsonResponse({'success': '0', 'message': 'Aadhaar number already registered'})
                    if Customer.objects.filter(pan_number=pan_num).exclude(unique_id=unique_id).exists():
                        return JsonResponse({'success': '0', 'message': 'PAN number already registered'})

                    login_id = request.session['login_id']
                    username = request.session['logged']

                    base_dir = os.path.join(settings.MEDIA_ROOT, f"customer/{unique_id}/")
                    os.makedirs(base_dir, exist_ok=True)

                    def save_image(file_obj, prefix):
                        ext = os.path.splitext(file_obj.name)[1]
                        filename = f"{prefix}{ext}"
                        path = os.path.join(base_dir, filename)
                        with open(path, 'wb+') as dest:
                            for chunk in file_obj.chunks():
                                dest.write(chunk)
                        return f"customer/{unique_id}/{filename}"

                    with transaction.atomic():
                        customer.name           = name
                        customer.mobile         = mobile
                        customer.email          = email
                        customer.aadhaar_number = aadhaar_num
                        customer.pan_number     = pan_num
                        customer.referral_code  = referral
                        customer.access         = access
                        customer.trading        = trading

                        if request.FILES.get('aadhaar_front_image'):
                            customer.aadhaar_front_image = save_image(request.FILES['aadhaar_front_image'], 'aadhaar_front')
                        if request.FILES.get('aadhaar_back_image'):
                            customer.aadhaar_back_image = save_image(request.FILES['aadhaar_back_image'], 'aadhaar_back')
                        if request.FILES.get('pan_front_image'):
                            customer.pan_front_image = save_image(request.FILES['pan_front_image'], 'pan_front')

                        customer.save()

                        # update addresses
                        addr_count = int(request.POST.get('addr_count', 0))
                        for idx in range(addr_count):
                            addr_uid = request.POST.get(f'addr_unique_id_{idx}', '').strip()
                            if not addr_uid:
                                continue
                            try:
                                addr = CustomerAddress.objects.get(unique_id=addr_uid, customer=customer)
                                addr.name          = request.POST.get(f'addr_name_{idx}', addr.name)
                                addr.mobile        = request.POST.get(f'addr_mobile_{idx}', addr.mobile)
                                addr.pincode       = request.POST.get(f'addr_pincode_{idx}', addr.pincode)
                                addr.state         = request.POST.get(f'addr_state_{idx}', addr.state)
                                addr.city          = request.POST.get(f'addr_city_{idx}', addr.city)
                                addr.district      = request.POST.get(f'addr_district_{idx}', addr.district)
                                addr.postoffice    = request.POST.get(f'addr_postoffice_{idx}', addr.postoffice)
                                addr.region        = request.POST.get(f'addr_region_{idx}', addr.region)
                                addr.address_line_1 = request.POST.get(f'addr_line1_{idx}', addr.address_line_1)
                                addr.address_line_2 = request.POST.get(f'addr_line2_{idx}', addr.address_line_2)
                                addr.save()
                            except CustomerAddress.DoesNotExist:
                                pass

                        util_obj.activity_log(login_id, username, "Customer Edit", f"Customer Updated => {unique_id}")

                    return JsonResponse({'success': '1', 'message': 'Customer updated successfully'})

                except Exception as e:
                    return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)

class OrderOperation:
    def getCustomerOrderDetails(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('customer_order_list') is not None:
                        order_id=request.POST["order_id"]

                        if order_id!="":
                            odrObj = Order.objects.filter(order_id = order_id)[0]

                            if odrObj:
                                data = cust_odr_obj.getOrderDetails(odrObj, order_id)
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

    def updateOrderStatus(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('btn_changeStatus') is not None:
                        order_id = request.POST.get("order_id")
                        date = request.POST.get("date")
                        order_status = request.POST.get("order_status")
                        chk_checked_prod_ids = request.POST.get("chk_checked_prod_ids")

                        if not (order_id and order_status and date and chk_checked_prod_ids):
                            return util_obj.printErrorResponse_200('Please fill all the mandatory fields!')
                            
                        # status_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                        status_date = util_obj.parse_date(date)
                        prod_ids = chk_checked_prod_ids.split(",")
                        valid_prod_ids = []
                        response = []

                        for pid in prod_ids:
                            try:
                                order_detail = OrderDetails.objects.get(order_id=order_id, prd_detail_id=pid)
                                
                                # Check valid status transitions
                                if order_detail.order_status == "Placed":
                                    if order_status in ["Approved", "Cancelled"]:
                                        valid_prod_ids.append(pid)
                                    else:
                                        response.append({"msg_type": "danger", "msg": f"<strong>{pid} is Placed => </strong> You can only change the status of Placed Order to Approved or Cancelled!"})

                                elif order_detail.order_status == "Approved":
                                    if order_status in ["Processed", "Cancelled"]:
                                        valid_prod_ids.append(pid)
                                    else:
                                        response.append({"msg_type": "danger", "msg": f"<strong>{pid} is Approved => </strong> You can only change the status of Approved Order to Processed or Cancelled!"})

                                elif order_detail.order_status == "Processed":
                                    if order_status in ["Dispatched", "Cancelled"]:
                                        valid_prod_ids.append(pid)
                                    else:
                                        response.append({"msg_type": "danger", "msg": f"<strong>{pid} is Processed => </strong> You can only change the status of Processed Order to Dispatched or Cancelled!"})

                                elif order_detail.order_status == "Dispatched":
                                    response.append({"msg_type": "danger", "msg": f"<strong>{pid} is Dispatched => </strong> You cannot change the status of a Dispatched Order!"})

                                elif order_detail.order_status == "Cancelled":
                                    response.append({"msg_type": "danger", "msg": f"<strong>{pid} is Cancelled => </strong> You cannot change the status of a Cancelled Order!"})

                            except OrderDetails.DoesNotExist:
                                response.append({"msg_type": "danger", "msg": f"<strong>{pid} => </strong> This product is not associated with this order!"})

                        # If there are valid products to update, proceed with transaction
                        if valid_prod_ids:
                            with transaction.atomic():
                                for vpd in valid_prod_ids:
                                    try:
                                        # Insert into OrderStatus table
                                        OrderStatus.objects.create(date=status_date, order_id=order_id, prd_detail_id=vpd, order_status=order_status)
                                        
                                        # Update OrderDetails table
                                        updated_count = OrderDetails.objects.filter(order_id=order_id, prd_detail_id=vpd).update(order_status=order_status)
                                        
                                        if updated_count > 0:
                                            response.append({"msg_type": "success", "msg": f"<strong>{vpd} => </strong> Order Status Updated!"})
                                        else:
                                            response.append({"msg_type": "danger", "msg": f"<strong>{vpd} => </strong> No changes detected!"})

                                    except Exception as e:
                                        response.append({"msg_type": "danger", "msg": f"<strong>{vpd} => </strong> Error updating order status!"})

                        return JsonResponse({"success": 1, "message": response})
                    else:
                        return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
                except:
                    return util_obj.printErrorResponse_200('Something went wrong. Please try again later.') 
            else:
                return util_obj.printErrorResponse_200('Something went wrong. Please try again later.')
        else:
            return util_obj.goToLogin(request)
        
class CartOperation:
    def getCustomerCartDetails(self,request):
        if util_obj.checkSession(request) == False:
            if request.method == 'POST':
                try:
                    if request.POST.get('customer_cart_list') is not None:
                        cart_id=request.POST["cart_id"]

                        if cart_id!="":
                            cartObj = Cart.objects.select_related("customer").filter(cart_id = cart_id)[0]

                            if cartObj:
                                data = cust_cart_obj.getCartDetails(cartObj, cart_id)
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

class PDFInvoice:
    def render_to_pdf(self, template_src, context_dict={}):
        template = get_template(template_src)
        html  = template.render(context_dict)
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
        if not pdf.err:
            return HttpResponse(result.getvalue(), content_type='application/pdf')
        return None
       
    def download_invoice(self, request, order_id, invoice_type='attachment'):
        if request.method == 'GET':
            invoice_data = Order.objects.filter(order_id__exact = order_id)[0]
            if invoice_data:
                data = cust_odr_obj.getOrderDetails(invoice_data, order_id)

                # print({'data':data})

                words = invoice_util.rupees_in_words(data[0]['sub_total'])
                    
                pdf = self.render_to_pdf('portal/pdf-reports/invoice.html', {'data':data,'rupees':words})
                response = HttpResponse(pdf, content_type='application/pdf')
                filename = "Invoice_%s.pdf" %(invoice_data.order_number)
                content = "%s; filename=%s" %(invoice_type, filename)
                response['Content-Disposition'] = content
                return response
            else:
                return render(request,'portal/404.html')


class InactiveCustomerCleanup:

    def _get_inactive_data(self):
        cutoff = timezone.now() - timedelta(days=30)

        never_recharged = Customer.objects.filter(
            date__lt=cutoff
        ).exclude(
            id__in=WalletRechargeHistory.objects.values_list('customer_id', flat=True)
        )

        recharge_cutoff_ids = WalletRechargeHistory.objects.filter(
            status='Success',
            created_at__gte=cutoff
        ).values_list('customer_id', flat=True)

        had_recharge_inactive = Customer.objects.filter(
            id__in=WalletRechargeHistory.objects.values_list('customer_id', flat=True)
        ).exclude(
            id__in=recharge_cutoff_ids
        ).filter(access='Granted')

        return cutoff, never_recharged, had_recharge_inactive

    def cleanup_page(self, request):
        if util_obj.checkSession(request) == False:
            return render(request, 'portal/inactive-customer-cleanup.html')
        return util_obj.goToLogin(request)

    def preview(self, request):
        if util_obj.checkSession(request) == False:
            try:
                cutoff, never_recharged, had_recharge_inactive = self._get_inactive_data()

                delete_list = list(never_recharged.values('unique_id', 'name', 'mobile', 'date')[:100])
                block_list  = list(had_recharge_inactive.values('unique_id', 'name', 'mobile', 'date')[:100])

                for row in delete_list:
                    row['date'] = timezone.localtime(row['date']).strftime('%d-%m-%Y') if row['date'] else ''
                for row in block_list:
                    row['date'] = timezone.localtime(row['date']).strftime('%d-%m-%Y') if row['date'] else ''

                return JsonResponse({
                    'success': '1',
                    'cutoff_date': cutoff.strftime('%d-%m-%Y'),
                    'delete_count': never_recharged.count(),
                    'block_count': had_recharge_inactive.count(),
                    'delete_list': delete_list,
                    'block_list': block_list,
                })
            except Exception as e:
                return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
        return util_obj.goToLogin(request)

    def run_cleanup(self, request):
        if util_obj.checkSession(request) == False:
            if request.method != 'POST':
                return JsonResponse({'success': '0', 'message': 'Invalid request'})
            try:
                username = request.session.get('logged', 'admin')
                login_id = request.session.get('login_id')

                _, never_recharged, had_recharge_inactive = self._get_inactive_data()

                delete_count = never_recharged.count()
                block_count  = had_recharge_inactive.count()

                with transaction.atomic():
                    deleted, _ = never_recharged.delete()
                    blocked    = had_recharge_inactive.update(access='Blocked')

                util_obj.activity_log(
                    login_id, username,
                    "Inactive Cleanup",
                    f"Deleted {deleted} inactive registrations | Blocked {blocked} inactive customers"
                )

                return JsonResponse({
                    'success': '1',
                    'message': f'Cleanup complete. Deleted: {deleted} | Blocked: {blocked}',
                    'deleted': deleted,
                    'blocked': blocked,
                })
            except Exception as e:
                return JsonResponse({'success': '0', 'message': 'Something went wrong', 'error': str(e)})
        return util_obj.goToLogin(request)