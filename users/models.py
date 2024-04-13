from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = "USER", "user"
        ADMIN = "ADMIN", "admin"


    base_role = Role.USER
    role = models.CharField(max_length=50, choices=Role.choices, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.role = self.base_role
        return super().save(*args, **kwargs)


class AdminManagger(BaseUserManager):
    def get_queryset(self, *args, **kwargs):
        results = super().get_queryset(*args, **kwargs)
        return results.filter(role=User.Role.ADMIN)


class Admin(User):
    base_role = User.Role.ADMIN

    Admin = AdminManagger()

    class Meta:
        proxy = True

    def welcome(self):
        return "Only for bookers"
