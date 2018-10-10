from django.contrib import admin
from helper import models

# Register your models here.
admin.site.register(models.Helper_user)
admin.site.register(models.Robot)
admin.site.register(models.Message)
admin.site.register(models.Setting)
