from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "user"
        CASHIER = "CASHIER", "cashier"
        CONSULTANT = "CONSULTANT", "consultant"
        BOOKER = "BOOKER", "booker"

    base_role = Role.USER
    role = models.CharField(max_length=50, choices=Role.choices, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class CashierManagger(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.CASHIER)


class Cashier(User):
    base_role = User.Role.CASHIER

    cashier = CashierManagger()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for Cashiers"


class ConsultantManagger(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.CONSULTANT)


class Consultant(User):
    base_role = User.Role.CONSULTANT

    consultant = ConsultantManagger()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for consultants"


class BookerManagger(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.BOOKER)


class Booker(User):
    base_role = User.Role.BOOKER

    booker = BookerManagger()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for bookers"
