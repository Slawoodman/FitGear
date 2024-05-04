from rest_framework import serializers
from market.models import Product, OrderItem, Order, Cart, CartItem, Category
from users.models import User


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["name"]


class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(many= False)
    class Meta:
        model = Product
        fields = "__all__"


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = CartItem
        fields = "__all__"


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(many=False)
    items = CartItemSerializer(many=True)  # No need for the source argument

    class Meta:
        model = Cart
        fields = "__all__"



class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=False)

    class Meta:
        model = OrderItem
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    customer = UserSerializer(many=False)
    order_items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = "__all__"
