'小助手的数据库设计'
import time
import datetime
from django.db import models


class Message(models.Model):
    '消息往来'
    text = models.CharField(max_length=200, default='')
    from_user = models.CharField(max_length=50, default='')
    to_user = models.CharField(max_length=50, default='')
    time = models.TimeField()
    message_type = models.CharField(max_length=10, default='TEXT')

    def __str__(self):
        return '%s-%s-%s' % (self.from_user, self.to_user, self.time)


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

    def get_start_time(self):
        '获取该课开始的时间'
        coursetime = COURSE_DICT[self.start - 1]
        weekday = self.weekday.index
        now = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        delta = datetime.timedelta(
            days=weekday - time.localtime().tm_wday,
            hours=coursetime[0], minutes=coursetime[1]
        )
        return time.mktime(datetime.datetime.timetuple(now + delta))

    def show_start_time(self):
        '以 "HOUR:MIN" 的格式显示上课时间'
        coursetime = COURSE_DICT[self.start - 1]
        return '%d:%d' % (coursetime[0], coursetime[1])


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


class Robot(models.Model):
    uin = models.CharField(max_length=50, default='', primary_key=True)
    nick_name = models.CharField(max_length=50, default='')

    def __str__(self):
        return '%s-%s' % (self.nick_name, self.uin)


class Helper_user(models.Model):
    '小助手用户'
    user_name = models.CharField(max_length=50, default='')
    nick_name = models.CharField(max_length=50, default='')
    user_id = models.EmailField(default='')
    password = models.CharField(max_length=50, default='')
    remind = models.IntegerField(default=0)
    remind_time = models.IntegerField(default=0)
    courses = models.ManyToManyField(Course, default=None)
    is_open = models.BooleanField(default=True)
    have_remind = models.BooleanField(default=False)
    wx_UserName = models.CharField(max_length=100, default='')
    robot = models.ForeignKey(Robot)

    def __str__(self):
        return str(self.user_name)

    def remind_update(self, week, is_flex=False, flex_day=0, count=0):
        '提醒列表更新'
        if week + count > END_WEEK:
            self.is_open = False
            self.save()
            raise NotImplementedError('%s本学期已经没有课了' % self.user_name)
        else:
            min_time_diff = None
            filter_condition = {"start_week__lt": week, 'end_week__gt': week}
            for course in self.courses.all().filter(**filter_condition):
                # if '课程名称' in course.name:
                #     course.name = course.name[5:]
                #     course.save()
                for coursetime in course.coursetimes.all():
                    time_diff = coursetime.get_start_time() - time.time() + 60 * 60 * 24 * 7 * count
                    if is_flex:
                        time_diff += (- flex_day +
                                      time.localtime().tm_wday) * 60 * 60 * 24
                    if time_diff > 0 and (min_time_diff is None or min_time_diff > time_diff):
                        self.remind = course.ident
                        self.remind_time = min_time_diff = int(time_diff)
            if min_time_diff is not None:
                self.save()
            else:
                return self.remind_update(week, is_flex, flex_day, count + 1)

    def courses_update(self, course_list):
        '课程列表更新'
        self.courses.clear()
        for ident in course_list:
            try:
                self.courses.add(Course.objects.get(ident=ident))
            except EXCEPTIONS:
                pass
        self.save()

    def set_alias(self, alias=None):
        import itchat
        itchat.set_alias(self.wx_UserName, alias if alias else self.user_name)


from .base import END_WEEK, COURSE_DICT, EXCEPTIONS
