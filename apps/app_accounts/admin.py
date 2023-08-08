from django.contrib import admin
from .models import User, Accountbyplanet, Memobyplanet

# Register your models here.

admin.site.register(User)
admin.site.register(Accountbyplanet)
admin.site.register(Memobyplanet)