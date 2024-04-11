# test_api.py

from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from market.models import Product, OrderItem

User = get_user_model()


class ChangeOrderStatusAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Create a product object
        product = Product.objects.create(name="Product", price=9.99)

        # Create an order item with a valid product
        order = OrderItem.objects.create(
            customer=self.user, product=product, status="Undecided"
        )

    def test_change_order_status(self):
        order_item = OrderItem.objects.first()
        url = reverse("change_order_status", args=[order_item.id])
        data = {"status": "Paid"}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Create a product object
        product = Product.objects.create(name="Product", price=9.99)

        # Create an order item with a valid product
        order = OrderItem.objects.create(
            customer=self.user, product=product, status="Undecided"
        )

    def test_get_order(self):
        order_item = OrderItem.objects.first()
        url = reverse("order", args=[order_item.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "Undecided")


class OrdersAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Create a product object
        product = Product.objects.create(name="Product", price=9.99)

        # Create an order item with a valid product
        order = OrderItem.objects.create(
            customer=self.user, product=product, status="Undecided"
        )

    def test_get_orders(self):
        url = reverse("orders")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class ProductAPIViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser", password="testpassword"
        )
        self.client.force_authenticate(user=self.user)

        # Create a product object
        Product.objects.create(name="Product", price=9.99)

    def test_get_product(self):
        product = Product.objects.first()
        url = reverse("product", args=[product.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["name"], "Product")
        self.assertEqual(response.data["price"], "9.99")
