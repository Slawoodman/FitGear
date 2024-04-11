from django import forms
from .models import OrderItem


class OrderCreatForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = ["address", "postal_code", "city"]
