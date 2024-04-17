from ckeditor.fields import RichTextField
from datetime import timedelta, datetime
from django.utils import timezone
from users.models import User
from django.db import models
from decimal import Decimal

RATING = (
    ( 1,  "★☆☆☆☆"),
    ( 2,  "★★☆☆☆"),
    ( 3,  "★★★☆☆"),
    ( 4,  "★★★★☆"),
    ( 5,  "★★★★★"),
)


class Product(models.Model):
    name = models.CharField(max_length=150, blank=True, null=True)
    image = models.ImageField(upload_to='products/', default='/default/image.jpg')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    short_description = models.TextField(max_length=200, blank=True, null=True)
    description = RichTextField()
    old_price = models.DecimalField(
        default=None, max_digits=10, decimal_places=2, blank=True, null=True
    )
    created = models.DateTimeField(
        auto_now_add=False, blank=True, null=True, default=timezone.now
    )

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        self.make_sale
        print(self.old_price)
        super().save(*args, **kwargs)


    @property
    def make_sale(self):
        if self.created and self.created.date() < timezone.now().date() - timedelta(
            days=30):
            self.old_price = self.price * Decimal(0.8)
            self.price =  self.price * Decimal(0.8)
        else:
            self.old_price = None


class ProductImages(models.Model):
    images = models.ImageField(upload_to="product-images", default="product.jpg")
    product = models.ForeignKey(Product, related_name="p_images", on_delete=models.SET_NULL, null=True)
    date = models.DateTimeField(auto_now_add=True)


    class Meta:
        verbose_name_plural = "Product Images"


class ProductInfo(models.Model):
    product = models.ForeignKey(Product, related_name="product_info", on_delete=models.SET_NULL, null=True)
    parametrs = models.CharField(max_length=100, null=True, blank=True)
    parameter_description = models.CharField(max_length=200, null=True, blank=True)


class ProductReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, related_name="reviews")
    review = models.TextField()
    rating = models.IntegerField(choices=RATING, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Product Reviews"

    def __str__(self):
        return self.product.name

    def get_rating(self):
        return self.rating


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return str(f"{self.user}'s cart")


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price_sum = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        self.price_sum = self.product.price * self.quantity
        super().save(*args, **kwargs)


class OrderItem(models.Model):
    STATUS_CHOICES = (
        ("Undecided", "UNDECIDED"),
        ("Paid", "PAID"),
        ("Completed", "COMPLETED"),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_item')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    address = models.CharField(max_length=250, default="")
    postal_code = models.CharField(max_length=20, default="")
    city = models.CharField(max_length=100, default="")
    created = models.DateTimeField(
        auto_now_add=False, blank=True, null=True, default=timezone.now
    )
    updated = models.DateTimeField(
        auto_now_add=False, blank=True, null=True, default=timezone.now
    )
    customer = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(default="", null=True, blank=True)
    is_paid = models.BooleanField(default=False, null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="Undecided")
    phone = models.CharField(max_length=20, default="")  # Поле для телефона

    def __str__(self):
        return f"OrderItem {self.id}"

    def save(self, *args, **kwargs):
        if self.product.discounted_price:
            self.price = self.product.discounted_price
        else:
            self.price = self.product.price
        return super().save(*args, **kwargs)

    def status_to_pading(self):
        if self.customer.role == 'ADMIN':
            self.status = "Paid"
            self.save()
        else:
            self.is_paid = True
            self.save()


