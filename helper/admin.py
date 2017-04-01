from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Helper_user)
admin.site.register(models.Course)
admin.site.register(models.Coursetime)
admin.site.register(models.Weekday)
