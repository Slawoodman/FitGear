from django import forms
from .models import Order, ProductReview


class OrderCreatForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["phone", "address", "postal_code", "department_number"]


class ReviewCreatForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["review", "rating"]

