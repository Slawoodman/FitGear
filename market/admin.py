from django.contrib import admin
from .models import Product, OrderItem


admin.site.register(Product)
admin.site.register(OrderItem)
