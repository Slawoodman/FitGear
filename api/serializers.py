from rest_framework import serializers
from market.models import Product, OrderItem
from users.models import User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)
    customer = UserSerializer(many=False)

    class Meta:
        model = OrderItem
        fields = "__all__"
