from django.db import models
from product.models import Category, Product
from customer.models import Customer, CustomerAddress

class Cart(models.Model):
    class Meta:
        db_table = 'cart'
    date = models.DateTimeField()
    cart_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    mobile = models.CharField(max_length=10, null=False)
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    cart_status = models.CharField(max_length=20, blank=False, default='Pending')
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)

class CartItems(models.Model):
    class Meta:
        db_table = 'cart_items'
    date = models.DateTimeField()
    cart = models.ForeignKey(Cart,to_field='cart_id',on_delete=models.SET_DEFAULT,default='undefined',related_name="cart_items")
    category = models.ForeignKey(Category,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    product = models.ForeignKey(Product,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    category_name = models.CharField(max_length=500, default='')
    product_name = models.CharField(max_length=500, default='')
    size = models.CharField(max_length=100, blank=False, null=False, default='')
    description = models.BinaryField()
    category_description = models.BinaryField()
    metal = models.CharField(max_length=100, blank=False, null=False, default='')
    metal_type = models.CharField(max_length=100, blank=False, null=False, default='')
    purity = models.CharField(max_length=100, blank=False, null=False, default='')
    price_per_10_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    weight_in_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    gst_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    making_fixed = models.CharField(max_length=20, blank=False, null=False)
    making_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    delivery_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    discount_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    quantity = models.IntegerField(null=False)
    price = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    total = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)

class Order(models.Model):
    class Meta:
        db_table = 'order'
    date = models.DateTimeField()
    order_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    order_number = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    cart = models.ForeignKey(Cart,to_field='cart_id',on_delete=models.SET_DEFAULT,default='undefined')
    mobile = models.CharField(max_length=10, null=False)
    customer = models.ForeignKey(Customer,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    address = models.ForeignKey(CustomerAddress,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    address_name = models.CharField(max_length=50, blank=False, null=True, default='')
    address_mobile = models.CharField(max_length=10, null=True)
    pincode = models.CharField(max_length=6,blank=False, null=False)
    postoffice = models.CharField(max_length=50, blank=False, null=False, default='')
    state = models.CharField(max_length=50, blank=False, null=False, default='')
    city = models.CharField(max_length=50, blank=False, null=False, default='')
    district = models.CharField(max_length=50, blank=False, null=False, default='')
    region = models.CharField(max_length=50, blank=False, null=False, default='')
    address_line_1 = models.CharField(max_length=255, blank=False, null=False, default='')
    address_line_2 = models.CharField(max_length=255, blank=False, null=False, default='')
    total_items = models.IntegerField(null=False)
    total_quantity = models.IntegerField(null=False)
    sub_total = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    remark = models.CharField(max_length=50, blank=False, null=False, default='')
    order_status = models.CharField(max_length=20, blank=False, default='Placed')
    token_logged_user = models.CharField(max_length=100, blank=False, default='', null=False)
    razorpay_order_id = models.CharField(max_length=32, blank=False, null=True, default='')
    razorpay_payment_id = models.CharField(max_length=32, blank=False, null=True, default='')
    payment_status = models.CharField(max_length=20, blank=False, default='Pending')
    
class OrderDetails(models.Model):
    class Meta:
        db_table = 'order_details'
    date = models.DateTimeField()
    order = models.ForeignKey(Order,to_field='order_id',on_delete=models.SET_DEFAULT,default='undefined')
    prd_detail_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    category = models.ForeignKey(Category,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    product = models.ForeignKey(Product,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    category_name = models.CharField(max_length=500, default='')
    product_name = models.CharField(max_length=500, default='')
    size = models.CharField(max_length=100, blank=False, null=False, default='')
    description = models.BinaryField()
    category_description = models.BinaryField()
    metal = models.CharField(max_length=100, blank=False, null=False, default='')
    metal_type = models.CharField(max_length=100, blank=False, null=False, default='')
    purity = models.CharField(max_length=100, blank=False, null=False, default='')
    price_per_10_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    weight_in_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    gst_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    making_fixed = models.CharField(max_length=20, blank=False, null=False)
    making_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    delivery_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    discount_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    quantity = models.IntegerField(null=False)
    price = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    total = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    order_status = models.CharField(max_length=20, blank=False, default='Placed')

class OrderStatus(models.Model):
    class Meta:
        db_table = 'order_status'
    date = models.DateTimeField()
    order = models.ForeignKey(Order,to_field='order_id',on_delete=models.SET_DEFAULT,default='undefined')
    prd_detail_id = models.CharField(max_length=32, blank=False, null=False, default='')
    order_status = models.CharField(max_length=20, blank=False)

# class OrderDocuments(models.Model):
#     class Meta:
#         db_table = 'order_documents'
#     date = models.DateTimeField()
#     order = models.ForeignKey(Order,to_field='order_id',on_delete=models.SET_DEFAULT,default='undefined')
#     document = models.CharField(max_length=700, blank=False, null=False, default='')
#     document_type = models.CharField(max_length=100, blank=False)