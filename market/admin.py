from django.contrib import admin
from .models import Product, OrderItem, ProductInfo, ProductImages, ProductReview


class ProductImagesAdmin(admin.TabularInline):
    model  = ProductImages


class ProductInfo(admin.TabularInline):
    model = ProductInfo 


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductInfo]


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']


admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem)
admin.site.register(ProductReview, ProductReviewAdmin)
