from django.test import TestCase, Client
from django.urls import reverse
from users.models import User
from market.models import Product, OrderItem
from django.core.management import call_command


class MarketTests(TestCase):
    fixtures = ["products.json"]

    def setUp(self):
        call_command("loaddata", "products.json")
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.product = Product.objects.create(name="Test Product", price=10)
        self.order_item = OrderItem.objects.create(
            product=self.product, customer=self.user
        )

    def test_main_page_view(self):
        response = self.client.get(reverse("main"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "market/main.html")

    def test_create_user_order_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("user-order", args=[self.product.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "market/order_form.html")

    def test_get_orders_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("showorders"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "market/order_list.html")

    def test_mark_order_item_as_paid_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("checkout", args=[self.order_item.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to showorders

    def test_change_order_status_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("change_status", args=[self.order_item.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "market/order_form.html")

    def test_generate_payment_html_view(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("genpayment", args=[self.order_item.pk]))
        self.assertEqual(response.status_code, 302)  # Redirects to showorders
