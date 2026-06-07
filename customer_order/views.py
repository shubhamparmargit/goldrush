from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from utility.views import Utility, RandomIdGenerate, Validation, current_date, urlPrefix, domainURL, domainURLPortal, InvoiceUtil
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connection, transaction
from django.conf import settings
from customer_order.models import Cart, CartItems, Order, OrderDetails, OrderStatus
from customer.models import Customer, CustomerAddress
from product.models import Category, Product, Product_Images
from product.views import ProductData
from collections import defaultdict
from datetime import datetime
from django.utils import timezone

# RazorPay
import razorpay
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

util_obj = Utility()
random_obj = RandomIdGenerate()
valid_obj = Validation()
prod_obj = ProductData()
invoice_util = InvoiceUtil()

class CustomerOrderData:
    # @api_view(['POST'])
    # @permission_classes([])
    # @authentication_classes([])
    # def create_razorpay_order(request):
    #     amount = int(request.POST['amount']) * 100  # Convert to paise
        
    #     order_data = {
    #         "amount": amount,
    #         "currency": "INR",
    #         "payment_capture": 1  # Auto capture
    #     }

    #     order = razorpay_client.order.create(order_data)
    #     return Response(order)

    def create_razorpay_order(self, amount):
        amount = int(amount) * 100  # Convert to paise

        order_data = {
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1  # Auto capture
        }

        order = razorpay_client.order.create(order_data)
        return order

    def generate_order_number(self):
        with transaction.atomic():
            now = datetime.now()
            year = str(now.year)[-2:]
            month = f"{now.month:02d}"

            prefix = f"GA/{year}/{month}/"

            last_order = (
                Order.objects
                .select_for_update()
                .filter(order_number__startswith=prefix)
                .order_by('-id')
                .first()
            )

            if last_order:
                try:
                    last_count = int(last_order.order_number.split('/')[-1])
                except:
                    last_count = 0
            else:
                last_count = 0

            new_count = last_count + 1

            return f"{prefix}{new_count:03d}"
    
    def updateOrderAfterPayment(self, order_id, razorpay_order_id, razorpay_payment_id, payment_status):
        updateOrder = Order.objects.filter(order_id = order_id, razorpay_order_id__exact = razorpay_order_id)
        if updateOrder:
            affected_rows = updateOrder.update(
                razorpay_payment_id = razorpay_payment_id,
                payment_status = payment_status
            )
            if affected_rows>0:
                return 1
            else:
                return 0

    def getOrderDetails(self, orderObj, order_id):
        data = []
        if orderObj:
            if orderObj.order_status=="Placed":
                cls='primary'
            elif orderObj.order_status=="Approved":
                cls='warning'
            elif orderObj.order_status=="Processed":
                cls='danger'
            elif orderObj.order_status=="Dispatched":
                cls='success'

            pay_cls = 'warning'
            if orderObj.payment_status == 'Success':
                pay_cls = 'success'
            elif orderObj.payment_status == 'Failed':
                pay_cls = 'danger'
                
            order_date_time = timezone.localtime(orderObj.date).strftime('%d-%m-%Y @ %I:%M %p')
            sub_total = util_obj.formatPrice(orderObj.sub_total)

            orderDetails = []
            status_details = []
            order_status_lst = []
            documentDetails = None

            sub_total_without_gst = 0
            gst_total = 0

            orderDetailObj = OrderDetails.objects.filter(order__order_id = order_id)
            if orderDetailObj:
                sr_no = 1
                for row in orderDetailObj:
                    price = invoice_util.money(row.price)
                    total = invoice_util.money(row.total)
                    if row.order_status=="Placed":
                        cls1='primary'
                    elif row.order_status=="Approved":
                        cls1='warning'
                    elif row.order_status=="Processed":
                        cls1='info'
                    elif row.order_status=="Dispatched":
                        cls1='success'
                    elif row.order_status=="Cancelled":
                        cls1='danger'

                    half_gst = invoice_util.money(row.gst_in_percent / 2)

                    calculatedPrice = prod_obj.calculate_price(row.price_per_10_gm, row.weight_in_gm, row.discount_in_percent, row.making_charge, row.delivery_charge, row.gst_in_percent)
                    half_gst_amount = invoice_util.money(calculatedPrice[3] / 2)
                    price_without_gst = invoice_util.money(row.quantity * calculatedPrice[1])

                    sub_total_without_gst = invoice_util.money(sub_total_without_gst + price_without_gst)
                    gst_total = invoice_util.money(gst_total + half_gst_amount)
                    
                    orderDetails.append({'sr_no':sr_no, 'product_detail_id':row.prd_detail_id, 'category_name':row.category_name, 'product_name':row.product_name,  'quantity':row.quantity, 'price':str(price), 'total':str(total), 'order_status':row.order_status, 'cls1':cls1, 'half_gst':str(half_gst), 'gst_amount':str(half_gst_amount), 'price_without_gst': str(price_without_gst)})

                    sr_no += 1

            order_status_arr=["Placed","Approved","Processed","Dispatched","Cancelled"]
            # Fetch order statuses
            statuses = OrderStatus.objects.filter(order_id=order_id).values("order_status", "date", "prd_detail_id")

            # Group product detail IDs by (order_status, date)
            status_dict = defaultdict(list)
            for status1 in statuses:
                key = (status1["order_status"], status1["date"])
                status_dict[key].append(status1["prd_detail_id"])

            # Format status details
            status_details = []
            for (order_status, date), prd_ids_list in status_dict.items():
                formatted_date = timezone.localtime(date).strftime('%d-%m-%Y @ %I:%M %p')
                status_details.append({
                    "order_status": order_status,
                    "date": formatted_date,
                    "prd_ids": ",".join(prd_ids_list)  # Manually concatenate product IDs
                })

            # Ensure all order statuses are included
            for os in order_status_arr:
                stDetails = [
                    {"date": s["date"], "prd_ids": s["prd_ids"]}
                    for s in status_details if s["order_status"] == os
                ]

                if not stDetails:
                    stDetails = [{"date": "NA", "prd_ids": "NA"}]

                order_status_lst.append({"order_status": os, "status_details": stDetails})


            # orderDocObj = OrderDocuments.objects.filter(order__order_id = order_id)
            # if orderDocObj:
            #     for row in orderDocObj:
            #         documentDetails.append({"document_name": os.path.basename(row.document),"document_type": row.document_type,"document": urlPrefix+row.document})

            invoice_url = domainURLPortal + 'download_invoice/' + orderObj.order_id + '/attachment'

            data.append({'success':'1','order_number':orderObj.order_number,'order_id':orderObj.order_id, 'order_date_time':order_date_time, 'remark':orderObj.remark, 'order_status':orderObj.order_status, 'cls':cls, 'razorpay_order_id':orderObj.razorpay_order_id, 'razorpay_payment_id':orderObj.razorpay_payment_id, 'payment_status':orderObj.payment_status, 'pay_cls':pay_cls, 'total_items':orderObj.total_items, 'total_quantity':orderObj.total_quantity, 'sub_total':str(invoice_util.money(sub_total)), 'address_name':orderObj.address_name, 'address_mobile':orderObj.address_mobile, 'pincode':orderObj.pincode, 'postoffice':orderObj.postoffice, 'state':orderObj.state, 'city':orderObj.city, 'district':orderObj.district, 'region':orderObj.region, 'address_line_1':orderObj.address_line_1, 'address_line_2':orderObj.address_line_2, 'customer_name':orderObj.customer.name, 'customer_mobile':orderObj.customer.mobile, 'customer_email':orderObj.customer.email, 'sub_total_without_gst':str(sub_total_without_gst), 'gst_total':str(gst_total), 'order_details':orderDetails, 'prod_order_status':order_status_lst, 'invoice_url':invoice_url})

        return data

class CustomerCartData:
    def getCartDetails(self, cartObj, cart_id):
        data = {}
        if cartObj:
            cart_date_time = timezone.localtime(cartObj.date).strftime('%d-%m-%Y @ %I:%M %p')
            if cartObj.cart_status=="Pending":
                cls='primary'
            elif cartObj.cart_status=="Processed":
                cls='success'
            cart_details = []
            cartItemObj = CartItems.objects.filter(cart__cart_id = cart_id)
            if cartItemObj:
                for row in cartItemObj:
                    product_image = ''
                    imageObj = Product_Images.objects.filter(product = row.product.unique_id)[0]
                    if imageObj:
                        product_image = urlPrefix+imageObj.image_url
                    formatted_price = str(invoice_util.money(row.price))
                    formatted_total = str(invoice_util.money(row.total))
                    date = timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
                    cart_details.append({'date':date,'product_id':row.product.unique_id, 'metal':row.metal, 'purity':row.purity, 'metal_type':row.metal_type, 'category':row.category_name, 'category_id':row.category.unique_id, 'name':row.product_name, 'size':row.size,'image':product_image, 'quantity':row.quantity, 'price':formatted_price, 'total':formatted_total})
            
            data = {'success':'1', 'cart_id':cart_id, 'cart_date':cart_date_time, 'customer_name':cartObj.customer.name, 'customer_mobile':cartObj.customer.mobile, 'customer_email':cartObj.customer.email, 'cart_status':cartObj.cart_status, 'cls':cls, 'cart_details':cart_details}
        return data
                
custOrderObj = CustomerOrderData() 
custCartObj = CustomerCartData()     

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def cartInsert(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            category_id = request.POST.get('category_id','')
            product_id = request.POST.get('product_id','')
            quantity = int(request.POST.get('quantity') or 0)
            
            if field == "" and mobile != "" and user_unique_id != "" and product_id != "" and category_id != "" and quantity != "":
                valid_obj.validate_mobile_number(mobile)
                valid_obj.validate_digits_multiple_keys(quantity = quantity)
                
                logged_user = request.user

                with transaction.atomic():
                    prodObj = Product.objects.select_related("category","metal","metal_type","purity").filter(access = 'Granted', unique_id = product_id, category__unique_id = category_id)
                    if prodObj:
                        total = quantity * prodObj[0].total_price

                        cartObj = Cart.objects.filter(cart_status = 'Pending', mobile = mobile, customer__unique_id = user_unique_id)
                        if cartObj:
                            cart_id = cartObj[0].cart_id
                            res = 0
                            cartItemObj = CartItems.objects.filter(cart__cart_id = cart_id, category__unique_id = category_id, product__unique_id = product_id)
                            if cartItemObj:
                                affected_rows = cartItemObj.update(
                                    category_name = prodObj[0].category.name,
                                    product_name = prodObj[0].name,
                                    size = prodObj[0].size,
                                    description = prodObj[0].description,
                                    category_description = prodObj[0].category_description,
                                    metal = prodObj[0].metal.metal_name,
                                    metal_type = prodObj[0].metal_type.type,
                                    purity = prodObj[0].purity.purity,
                                    price_per_10_gm = prodObj[0].price_per_10_gm,
                                    weight_in_gm = prodObj[0].weight_in_gm,
                                    gst_in_percent = prodObj[0].gst_in_percent,
                                    making_fixed = prodObj[0].making_fixed,
                                    making_charge = prodObj[0].making_charge,
                                    delivery_charge = prodObj[0].delivery_charge,
                                    discount_in_percent = prodObj[0].discount_in_percent,
                                    quantity = quantity,
                                    price = prodObj[0].total_price,
                                    total = total
                                )
                                if affected_rows>0:
                                    res = 1
                            else:
                                insertCartItemData = CartItems.objects.create(
                                    date = current_date,
                                    cart = Cart.objects.get(cart_id = cart_id),
                                    category = Category.objects.get(unique_id=category_id),
                                    product = Product.objects.get(unique_id=product_id),
                                    category_name = prodObj[0].category.name,
                                    product_name = prodObj[0].name,
                                    size = prodObj[0].size,
                                    description = prodObj[0].description,
                                    category_description = prodObj[0].category_description,
                                    metal = prodObj[0].metal.metal_name,
                                    metal_type = prodObj[0].metal_type.type,
                                    purity = prodObj[0].purity.purity,
                                    price_per_10_gm = prodObj[0].price_per_10_gm,
                                    weight_in_gm = prodObj[0].weight_in_gm,
                                    gst_in_percent = prodObj[0].gst_in_percent,
                                    making_fixed = prodObj[0].making_fixed,
                                    making_charge = prodObj[0].making_charge,
                                    delivery_charge = prodObj[0].delivery_charge,
                                    discount_in_percent = prodObj[0].discount_in_percent,
                                    quantity = quantity,
                                    price = prodObj[0].total_price,
                                    total = total
                                )
                                if insertCartItemData:
                                    res = 1

                            if res == 1:
                                return Response({'success':'1','message':'Cart data added successfully'}, status=status.HTTP_200_OK)
                            else:
                                return Response({'success':'0','message':'Error adding new cart data'}, status=status.HTTP_200_OK)
                        else:
                            cart_id = 'cart_'+str(random_obj.generateUID())

                            insertCartData = Cart.objects.create(
                                date = current_date,
                                cart_id = cart_id,
                                mobile = mobile,
                                customer = Customer.objects.get(unique_id=user_unique_id),
                                token_logged_user = logged_user
                            )
                            if insertCartData:
                                insertCartItemData = CartItems.objects.create(
                                    date = current_date,
                                    cart = Cart.objects.get(cart_id = cart_id),
                                    category = Category.objects.get(unique_id=category_id),
                                    product = Product.objects.get(unique_id=product_id),
                                    category_name = prodObj[0].category.name,
                                    product_name = prodObj[0].name,
                                    size = prodObj[0].size,
                                    description = prodObj[0].description,
                                    category_description = prodObj[0].category_description,
                                    metal = prodObj[0].metal.metal_name,
                                    metal_type = prodObj[0].metal_type.type,
                                    purity = prodObj[0].purity.purity,
                                    price_per_10_gm = prodObj[0].price_per_10_gm,
                                    weight_in_gm = prodObj[0].weight_in_gm,
                                    gst_in_percent = prodObj[0].gst_in_percent,
                                    making_fixed = prodObj[0].making_fixed,
                                    making_charge = prodObj[0].making_charge,
                                    delivery_charge = prodObj[0].delivery_charge,
                                    discount_in_percent = prodObj[0].discount_in_percent,
                                    quantity = quantity,
                                    price = prodObj[0].total_price,
                                    total = total
                                )
                                if insertCartItemData:
                                    return Response({'success':'1','message':'Cart data added successfully'}, status=status.HTTP_200_OK)
                                else:
                                    return Response({'success':'0','message':'Error adding new cart data'}, status=status.HTTP_200_OK)
                            else:
                                return Response({'success':'0','message':'Error adding new cart data'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'No data found for given details'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK) 

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def customerCartData(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            
            if field == "" and mobile != "" and user_unique_id != "":
                cartObj = Cart.objects.select_related("customer").filter(cart_status = 'Pending', mobile = mobile, customer__unique_id = user_unique_id)
                if cartObj:
                    cart_id = cartObj[0].cart_id
                    data = custCartObj.getCartDetails(cartObj[0], cart_id)
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
def cartDelete(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            cart_id = request.POST.get('cart_id','')
            category_id = request.POST.get('category_id','')
            product_id = request.POST.get('product_id','')
            
            if field == "" and mobile != "" and user_unique_id != "" and product_id != "" and category_id != "" and cart_id != "":
                valid_obj.validate_mobile_number(mobile)

                with connection.cursor() as cursor, transaction.atomic():
                    cartItemObj = CartItems.objects.filter(cart__cart_id = cart_id, category__unique_id = category_id, product__unique_id = product_id)
                    if cartItemObj:
                        deleted_count, _ = cartItemObj.delete()
                        
                        if deleted_count > 0:
                            cursor.execute("update cart set cart_status='Discarded' where cart_id=%s and (select count(*) from cart_items where cart_id=%s)=0", [cart_id, cart_id])
                            return Response({'success':'1','message':'Cart data added successfully'}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':'0','message':'Error deleting cart data'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'No data found for given details'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)    

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def placeOrder(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            cart_id = request.POST.get('cart_id','')
            address_id = request.POST.get('address_id','')
            remark = request.POST.get('remark')
            
            if field == "" and mobile != "" and user_unique_id != "" and cart_id != "" and address_id != "":
                valid_obj.validate_mobile_number(mobile)
                
                order_id = random_obj.generate_order_id()
                order_number = custOrderObj.generate_order_number()
                logged_user = request.user

                with transaction.atomic():
                    addObj = CustomerAddress.objects.filter(unique_id = address_id, customer__unique_id = user_unique_id)
                    if addObj:
                        total_items = 0
                        total_quantity = 0
                        sub_total = 0
                        data_arr = []
                        orderStatus_arr = []

                        insertData = Order.objects.create(
                            date = current_date,
                            order_id = order_id,
                            order_number = order_number,
                            cart = Cart.objects.get(cart_id = cart_id),
                            mobile = mobile,
                            customer = Customer.objects.get(unique_id=user_unique_id),
                            address = CustomerAddress.objects.get(unique_id=address_id),
                            address_name = addObj[0].name,
                            address_mobile = addObj[0].mobile,
                            pincode = addObj[0].pincode,
                            postoffice = addObj[0].postoffice,
                            state = addObj[0].state,
                            city = addObj[0].city,
                            district = addObj[0].district,
                            region = addObj[0].region,
                            address_line_1 = addObj[0].address_line_1,
                            address_line_2 = addObj[0].address_line_2,
                            total_items = total_items,
                            total_quantity = total_quantity,
                            sub_total = sub_total,
                            remark = remark,                            
                            token_logged_user = logged_user
                        )
                        if insertData:
                            cartItemObj = CartItems.objects.select_related('cart').filter(cart__cart_id = cart_id, cart__customer__unique_id = user_unique_id, cart__cart_status = 'Pending')
                            if cartItemObj:
                                for row in cartItemObj:
                                    total_items += 1
                                    prd_detail_id = order_number+"-"+str(total_items)
                                    sub_total = sub_total + row.total
                                    total_quantity = total_quantity + row.quantity

                                    data_arr.append(OrderDetails(date = current_date, order = Order.objects.get(order_id = order_id), prd_detail_id = prd_detail_id, category = Category.objects.get(unique_id=row.category.unique_id), product = Product.objects.get(unique_id=row.product.unique_id), size = row.size, description = row.description, category_description = row.category_description, metal = row.metal, metal_type = row.metal_type, purity = row.purity, price_per_10_gm = row.price_per_10_gm, weight_in_gm = row.weight_in_gm, gst_in_percent = row.gst_in_percent, making_fixed = row.making_fixed, making_charge = row.making_charge, delivery_charge = row.delivery_charge, discount_in_percent = row.discount_in_percent, quantity = row.quantity, price = row.price, total = row.total, category_name = row.category_name,product_name = row.product_name))

                                    orderStatus_arr.append(OrderStatus(date = current_date, order = Order.objects.get(order_id = order_id), prd_detail_id = prd_detail_id, order_status = 'Placed'))
                            else:
                                return Response({'success':'0','message':'No data found for given details'}, status=status.HTTP_200_OK)
                            
                            razorpay_order_id = ''
                            razorpayOrder = custOrderObj.create_razorpay_order(sub_total)
                            if len(razorpayOrder) > 0:
                                razorpay_order_id = razorpayOrder["id"]

                                updateOrder = Order.objects.filter(order_id = order_id)
                                if updateOrder:
                                    affected_rows = updateOrder.update(
                                        total_items = total_items,
                                        total_quantity = total_quantity,
                                        sub_total = sub_total,
                                        razorpay_order_id = razorpay_order_id
                                    )
                                    if affected_rows>0:
                                        pass

                                orderDetailsObj = OrderDetails.objects.bulk_create(data_arr, ignore_conflicts=True)

                                if orderDetailsObj:  
                                    orderStatusObj = OrderStatus.objects.bulk_create(orderStatus_arr, ignore_conflicts=True)

                                    if orderStatusObj:
                                        cartObj = Cart.objects.filter(cart_id = cart_id)
                                        if cartObj:
                                            affected_rows = cartObj.update(
                                                cart_status = 'Processed'
                                            )
                                            if affected_rows>0:
                                                return Response({'success':'1','message':'Order Placed Successfully.','order_number':order_number,'order_id':order_id, 'razorpay_order_id' : razorpay_order_id, 'order_amount':sub_total}, status=status.HTTP_200_OK)
                                            else:
                                                return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                                        else:
                                            return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                                    else:
                                        return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                                else:
                                    return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                            else:
                                return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                        else:
                           return Response({'success':'0','message':'Error placing order'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'No data found for given details'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'success':'0','message':"ERROR:"+str(e)}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def verify_payment(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            order_id = request.POST.get('order_id','')
            razorpay_order_id = request.POST.get('razorpay_order_id','')
            razorpay_payment_id = request.POST.get('razorpay_payment_id','')
            razorpay_signature = request.POST.get('razorpay_signature','')

            if field == "" and mobile != "" and user_unique_id != "" and order_id != "" and razorpay_order_id != "" and razorpay_payment_id != "" and razorpay_signature != "":
                data = {
                    "razorpay_order_id": razorpay_order_id,
                    "razorpay_payment_id": razorpay_payment_id,
                    "razorpay_signature": razorpay_signature
                }

                payment_status = 'Failed'
                custOrderObj.updateOrderAfterPayment(order_id, razorpay_order_id, razorpay_payment_id, payment_status)

                try:
                    razorpay_client.utility.verify_payment_signature(data)
                    payment_status = 'Success'
                    res = custOrderObj.updateOrderAfterPayment(order_id, razorpay_order_id, razorpay_payment_id, payment_status)
                    if res == 1:
                        return Response({'success':'1','message':'Payment done successfully.'}, status=status.HTTP_200_OK)
                    else:
                        return Response({'success':'0','message':'Payment Failed'}, status=status.HTTP_200_OK)
                except razorpay.errors.SignatureVerificationError:
                    return Response({'success':'0','message':'Payment Failed'}, status=status.HTTP_200_OK) 

            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except IntegrityError as e: 
            return Response({'success': '0', 'message': 'Duplicate entry detected.'}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([TokenAuthentication])
def orderList(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            present_order = request.POST.get('present_order','')
            
            if field == "" and mobile != "" and user_unique_id != "" and present_order != "" and present_order in ['Yes','No']:
                order_history_arr=["Dispatched","Cancelled"]
                order_present_arr=["Placed","Approved","Processed"]
                
                if present_order == 'Yes':
                    orderObj = Order.objects.filter(mobile = mobile, customer__unique_id = user_unique_id, order_status__in = order_present_arr)
                else:
                    orderObj = Order.objects.filter(mobile = mobile, customer__unique_id = user_unique_id, order_status__in = order_history_arr)

                if orderObj:
                    data = []
                    for row in orderObj:
                        order_date_time = timezone.localtime(row.date).strftime('%d-%m-%Y @ %I:%M %p')
                        sub_total = str(invoice_util.money(row.sub_total))
                        data.append({'order_number':row.order_number,'order_id':row.order_id, 'order_date_time':order_date_time, 'total_items':row.total_items, 'total_quantity':row.total_quantity, 'sub_total':sub_total, 'order_status':row.order_status})
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
def orderDetails(request):
    if request.method == 'POST':
        try:
            field=request.POST['field']
            mobile = request.POST.get('mobile','')
            user_unique_id = request.POST.get('user_unique_id','')
            order_id = request.POST.get('order_id','')
            
            if field == "" and mobile != "" and user_unique_id != "" and order_id != "":
                orderObj = Order.objects.filter(mobile = mobile, customer__unique_id = user_unique_id, order_id = order_id)[0]
                if orderObj:
                    data = custOrderObj.getOrderDetails(orderObj, order_id)
                    return Response(data, status=status.HTTP_200_OK)
                else:
                    return Response({'success':'0','message':'No data found'}, status=status.HTTP_200_OK)
            else:
                return Response({'success':'0','message':'Please fill all the mandatory fields.'}, status=status.HTTP_200_OK)
        except ValidationError as e: 
            return Response({'success':'0','message':f"{e.message}"}, status=status.HTTP_200_OK)
        except:
            return Response({'success':'0','message':'Something went wrong. Please try again later.'}, status=status.HTTP_200_OK)  