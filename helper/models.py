from django.db import models

class Weekday(models.Model):
    '星期几'
    index = models.IntegerField(primary_key=True)
    day = models.CharField(max_length=5)

    def __str__(self):
        return str(self.day)

class Coursetime(models.Model):
    '上课时间'
    weekday = models.ForeignKey(Weekday)
    start = models.IntegerField()
    end = models.IntegerField()

    def __str__(self):
        return '%s %d-%d' % (self.weekday, self.start, self.end)

class Course(models.Model):
    '课程'
    ident = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=20)
    place = models.CharField(max_length=20)
    start_week = models.IntegerField(default=0)
    end_week = models.IntegerField(default=20)
    coursetimes = models.ManyToManyField(Coursetime)

    def __str__(self):
        return str(self.ident)

class Helper_User(models.Model):
    '小助手用户'
    user_name = models.CharField(max_length=20)
    user_id = models.EmailField()
    password = models.CharField(max_length=20)
    nick_name = models.CharField(max_length=20)
    course_list = models.TextField(default='[]')
    remind_list = models.TextField(default='[]')
    courses = models.ManyToManyField(Course, default=None)
    is_open = models.BooleanField(default=True)
    have_remind = models.BooleanField(default=False)
    wx_UserName = models.CharField(max_length=50, default='')

    def __str__(self):
        return str(self.nick_name)
