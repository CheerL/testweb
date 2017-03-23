from django.db import models

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
