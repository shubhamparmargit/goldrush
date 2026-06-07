from django.db import models

class Metal(models.Model):
    class Meta:
        db_table = 'metal'
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    metal_name = models.CharField(max_length=100, blank=False, null=False, unique=True, default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class MetalPurity(models.Model):
    class Meta:
        db_table = 'metal_purity'
        constraints = [
            models.UniqueConstraint(fields=['purity', 'metal'], name='unique_metal_purity')
        ]
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    purity = models.CharField(max_length=100, blank=False, default='')
    metal = models.ForeignKey(Metal,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class MetalType(models.Model):
    class Meta:
        db_table = 'metal_type'
        constraints = [
            models.UniqueConstraint(fields=['type', 'metal'], name='unique_metal_type')
        ]
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    type = models.CharField(max_length=100, blank=False, default='')
    metal = models.ForeignKey(Metal,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class MetalPurityPrice(models.Model):
    class Meta:
        db_table = 'metal_purity_price'
        constraints = [
            models.UniqueConstraint(fields=['purity', 'metal'], name='unique_metal_purity_price')
        ]    
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    price_per_10_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    metal = models.ForeignKey(Metal,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    purity = models.ForeignKey(MetalPurity,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class Unit(models.Model):
    class Meta:
        db_table = 'unit'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    unit_name = models.CharField(max_length=100, blank=False, null=False, unique=True, default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class GenderCategories(models.Model):
    class Meta:
        db_table = 'gender_categories'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    gender_name = models.CharField(max_length=100, blank=False, null=False, unique=True, default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')
    
class Category(models.Model):
    class Meta:
        db_table = 'category'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    name = models.CharField(max_length=500, blank=False, null=False, unique=True, default='')
    image = models.CharField(max_length=700)
    gender_categories = models.ManyToManyField(GenderCategories, related_name='categories')
    access = models.CharField(max_length=20, blank=False, default='Blocked')

class Product(models.Model):
    class Meta:
        db_table = 'product'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    name = models.CharField(max_length=500, blank=False, null=False, unique=True, default='')
    category = models.ForeignKey(Category,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    size = models.CharField(max_length=100, blank=False, null=False, default='')
    access = models.CharField(max_length=20, blank=False, default='Blocked')
    hot_sale = models.CharField(max_length=20, blank=False, default='No')
    description = models.BinaryField()
    category_description = models.BinaryField()
    metal = models.ForeignKey(Metal,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    metal_type = models.ForeignKey(MetalType,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    purity = models.ForeignKey(MetalPurity,to_field='unique_id',on_delete=models.SET_DEFAULT,default='')
    price_per_10_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    weight_in_gm = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    gst_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    making_fixed = models.CharField(max_length=20, blank=False, default='No')
    making_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    delivery_charge = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    discount_in_percent = models.DecimalField(max_digits=20, decimal_places=4, null=False, blank=False)
    total_price = models.DecimalField(max_digits=20, decimal_places=4, null=True)

class Product_Images(models.Model):
    class Meta:
        db_table = 'product_images'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    image_url = models.CharField(max_length=300, blank=False, default='')
    image_type = models.CharField(max_length=50, blank=False, default='')
    product = models.ForeignKey(Product,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    added_by = models.CharField(max_length=50, blank=False, default='')

class Product_Videos(models.Model):
    class Meta:
        db_table = 'product_videos'
    date = models.DateTimeField()
    unique_id = models.CharField(max_length=32, blank=False, unique=True, null=False, default='')
    video_url = models.CharField(max_length=300, blank=False, default='')
    product = models.ForeignKey(Product,to_field='unique_id',on_delete=models.SET_DEFAULT,default='undefined')
    added_by = models.CharField(max_length=50, blank=False, default='')

class Stock(models.Model):
    class Meta:
        db_table = 'stock'
    product = models.OneToOneField(Product,to_field='unique_id', on_delete=models.CASCADE, related_name='stock')
    quantity = models.IntegerField(default=0)
    last_updated = models.DateTimeField()
    added_by = models.CharField(max_length=50, blank=False, default='')

class StockMovement(models.Model):
    class Meta:
        db_table = 'stock_movement'
    MOVEMENT_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
    ]
    product = models.ForeignKey(Product,to_field='unique_id', on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=3, choices=MOVEMENT_TYPES)
    quantity = models.IntegerField()
    reference = models.CharField(max_length=255, null=True, blank=True)
    movement_date = models.DateTimeField()
    added_by = models.CharField(max_length=50, blank=False, default='')
