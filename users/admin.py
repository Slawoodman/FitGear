from django.contrib import admin
from .models import User, Cashier, Consultant, Booker

admin.site.register(User)
admin.site.register(Cashier)
admin.site.register(Consultant)
admin.site.register(Booker)
