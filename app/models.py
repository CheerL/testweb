from django.db import models
from django.contrib import admin

class Helper_User(models.Model):
    user_name = models.CharField(max_length=20)
    user_id = models.EmailField()
    password = models.CharField(max_length=20)
    nick_name = models.CharField(max_length=20)
    course_list = models.TextField(default='[]')
    is_open = models.BooleanField(default=True)
    have_remind = models.BooleanField(default=False)

    def __str__(self):
        return "%s" % self.nick_name
