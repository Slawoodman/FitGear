from django.contrib import admin
from .models import Product, OrderItem, ProductInfo, ProductImages, ProductReview, Cart, CartItem


class ProductImagesAdmin(admin.TabularInline):
    model  = ProductImages


class ProductInfo(admin.TabularInline):
    model = ProductInfo 


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImagesAdmin, ProductInfo]


class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'review', 'rating']


class CartItemsAdmin(admin.TabularInline):
    model = CartItem


class CartAdmin(admin.ModelAdmin):
    inlines = [CartItemsAdmin]

admin.site.register(Product, ProductAdmin)
admin.site.register(OrderItem)
admin.site.register(ProductReview, ProductReviewAdmin)
admin.site.register(Cart, CartAdmin)
