from django.contrib import admin
from .models import Category, Shop, ShopBankDetail, Shop_product, Product, ProductAccountDetail, ProductImage, ShopReview, ProductReview

admin.site.register(Category)
admin.site.register(Shop)
admin.site.register(ShopBankDetail)
admin.site.register(Shop_product)
admin.site.register(Product)
admin.site.register(ProductAccountDetail)
admin.site.register(ProductImage)
admin.site.register(ShopReview)
admin.site.register(ProductReview)