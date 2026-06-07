from product.views import *
from django.urls import include, re_path, path

page_obj = Pages()
metal_obj = MetalData()
purity_obj = MetalPurityData()
type_obj = MetalTypeData()
price_obj = PurityPrice()
unit_obj = UnitData()
gen_obj = GenderData()
cat_obj = CategoryData()
prod_obj = ProductData()
stock_obj = StockOperation()

urlpatterns = [
    re_path(r'^metal-purity-price$', page_obj.metal_purity_price, name='metal_purity_price'),
    re_path(r'^unit$', page_obj.unit, name='unit'),
    re_path(r'^category$', page_obj.category, name='category'),
    re_path(r'^product$', page_obj.add_product, name='add_product'),
    re_path(r'^product-list$', page_obj.product_list, name='product_list'),
    re_path(r'^update-product$', page_obj.update_product, name='update_product'),
    re_path(r'^product-stock$', page_obj.product_stock, name='product_stock'),
    # path('stock-movement/<slug:product>', page_obj.stock_movement, name='stock_movement'),
    re_path(r'^set-product-session$', page_obj.set_product_session, name="set_product_session"),
    re_path(r'^stock-movement$', page_obj.stock_movement, name='stock_movement'),

    re_path(r'^metal-list$', metal_obj.getAllMetals, name='metal_list'),

    re_path(r'^purity-list$', purity_obj.getPurityByMetal, name='purity_list'),

    re_path(r'^type-list$', type_obj.getTypeByMetal, name='type_list'),

    re_path(r'^gender-category-list$', gen_obj.getAllGenders, name='getAllGenders'),

    re_path(r'^addPurityPrice$', price_obj.addPurityPrice, name='addPurityPrice'),
    re_path(r'^getPurityPrice$', price_obj.getPurityPrice, name='getPurityPrice'),
    re_path(r'^updatePurityPrice$', price_obj.updatePurityPrice, name='updatePurityPrice'),
    re_path(r'^getMetalPurityPrice$', price_obj.getMetalPurityPrice, name='getMetalPurityPrice'),

    re_path(r'^addUnit$', unit_obj.addUnit, name='addUnit'),
    re_path(r'^getUnit$', unit_obj.getUnit, name='getUnit'),
    re_path(r'^updateUnit$', unit_obj.updateUnit, name='updateUnit'),

    re_path(r'^addCategory$', cat_obj.addCategory, name='addCategory'),
    re_path(r'^getCategory$', cat_obj.getCategory, name='getCategory'),
    re_path(r'^updateCategory$', cat_obj.updateCategory, name='updateCategory'),
    re_path(r'^category-list$', cat_obj.getAllCategory, name='getAllCategory'),

    re_path(r'^addProduct$', prod_obj.addProduct, name='addProduct'),
    re_path(r'^updateProduct$', prod_obj.updateProduct, name='updateProduct'),
    re_path(r'^getAllProduct$', prod_obj.getAllProduct, name='getAllProduct'),
    re_path(r'^uploadProductImages$', prod_obj.uploadProductImages, name='uploadProductImages'),
    re_path(r'^uploadVideos$', prod_obj.uploadVideos, name='uploadVideos'),
    re_path(r'^showProductImages$', prod_obj.showProductImages, name='showProductImages'),
    re_path(r'^showVideos$', prod_obj.showVideos, name='showVideos'),
    re_path(r'^deleteProductImage$', prod_obj.deleteProductImage, name='deleteProductImage'),
    re_path(r'^deleteVideo$', prod_obj.deleteVideo, name='deleteVideo'),

    re_path(r'^addStock$', stock_obj.addStock, name='addStock'),
]