'小助手的数据库设计'
import datetime
import time
from ast import literal_eval

from django.db import models

from helper.consumers import group_send
from helper.setting import COURSE_DICT, END_WEEK, EXCEPTIONS


class Setting(models.Model):
    rebot_reply = models.BooleanField(default=False)
    voice_reply = models.BooleanField(default=False)

    def change_settings(self, items):
        self.voice_reply = items['VOICE_REPLY']
        self.rebot_reply = items['ROBOT_REPLY']
        self.save()

    def json(self):
        return {
            'VOICE_REPLY': self.voice_reply,
            'ROBOT_REPLY': self.rebot_reply
        }


class Robot(models.Model):
    '机器人用户'
    uin = models.CharField(max_length=50, default='', primary_key=True)
    nick_name = models.CharField(max_length=50, default='')
    settings = models.ForeignKey(Setting, default='None', on_delete=models.CASCADE)

    def __str__(self):
        return '%s-%s' % (self.nick_name, self.uin)


class Message(models.Model):
    '消息往来'
    text = models.CharField(max_length=200, default='')
    user = models.CharField(max_length=50, default='')
    robot = models.ForeignKey(Robot, default='None', on_delete=models.CASCADE)
    time = models.DateTimeField(auto_now_add=True)
    message_type = models.CharField(max_length=10, default='TEXT')
    direction = models.CharField(max_length=10, default='IN')

    def __str__(self):
        return '%s-%s-%s' % (self.user, self.robot.nick_name, self.time)

    async def send_to_client(self):
        channel = 'chat-%s' % self.robot.nick_name
        await group_send(channel, dict(
            text=self.text,
            name=self.user,
            direction=self.direction,
            sender=self.robot.nick_name if self.direction == 'OUT' else self.user,
            IN=False if self.direction == 'OUT' else True,
            time=str(self.time)
        ))

class Helper_user(models.Model):
    '小助手用户'
    user_name = models.CharField(max_length=50, default='')
    nick_name = models.CharField(max_length=50, default='')
    user_id = models.EmailField(default='')
    password = models.CharField(max_length=50, default='')
    remind = models.IntegerField(default=0)
    remind_time = models.IntegerField(default=0)
    is_open = models.BooleanField(default=True)
    have_remind = models.BooleanField(default=False)
    wx_UserName = models.CharField(max_length=100, default='')
    robot = models.ForeignKey(Robot, default='None', on_delete=models.CASCADE)

    def __str__(self):
        return str(self.user_name)

    def set_alias(self, alias=None):
        from helper.async_itchat import async_itchat as itchat
        itchat.set_alias(self.wx_UserName, alias if alias else self.user_name)
