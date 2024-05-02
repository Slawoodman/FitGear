from django import forms
from .models import Order, ProductReview


class OrderCreatForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ["address", "postal_code", "city"]


class ReviewCreatForm(forms.ModelForm):
    class Meta:
        model = ProductReview
        fields = ["review", "rating"]
