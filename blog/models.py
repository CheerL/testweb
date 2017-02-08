from django.db import models
from django.contrib import admin

# Create your models here.
class Blogs(models.Model):
    title = models.CharField(max_length=150)
    body = models.TextField()
    date = models.DateField()
    category = models.CharField(max_length=10)

    def __str__(self):
        return self.title

class Categorys(models.Model):
    name = models.CharField(max_length=10)
    count = models.IntegerField()

    def __str__(self):
        return self.name

admin.site.register(Blogs)
admin.site.register(Categorys)
