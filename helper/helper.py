# _*_ coding: utf-8 _*_
'小助手'
import os
import time

import itchat
import requests

from helper.consumers import group_send
from helper.models import Helper_user, Message
from helper.setting import EXCEPTIONS, LOG_PATH, TL_KEY, HELPER_PKL
from helper.utils import logger


class HelperLogger(logger.Logger):
    async def info(self, msg, is_report=False):
        '向文件输出日志, 并发送到log频道'
        super().info(msg)
        try:
            await group_send('log', {'msg': msg})
        except EXCEPTIONS:
            pass
        if is_report:
            raise NotImplementedError(msg)

    def log_read(self, count=1, start=0):
        '从倒数start行读取count行日志, 返回一个列表'
        file_name = os.path.join(self.log_path, '{name}.log'.format(name=self.name))
        if not os.path.exists(file_name):
            with open(file_name, 'w+'):
                pass
        with open(file_name, 'r') as file:
            content = file.readlines()
            if count is -1 and start is 0:
                line_list = content[::-1]
            else:
                line_list = content[-1 - start:-1 - start - count:-1]
        return line_list

class Helper:
    '助手类'
    robot = None
    logger = HelperLogger('itchat', LOG_PATH)

    def __init__(self):
        self.IS_LOGIN = False
        self.settings = Setting(self)
        self.user = None

    @staticmethod
    def get_head_img(user_name, pic_dir, name):
        '获取用户头像'
        if not os.path.exists(pic_dir) or (time.time() - os.path.getctime(pic_dir) > 24 * 60 * 60):
            try:
                itchat.get_head_img(userName=user_name, picDir=pic_dir)
            except:
                pass

    @staticmethod
    def get_robot_response(msg):
        '这里我们就像在“3. 实现最简单的与图灵机器人的交互”中做的一样'
        # 构造了要发送给服务器的数据
        api_url = 'http://www.tuling123.com/openapi/api'
        data = {
            'key': TL_KEY,
            'info': msg,
            'userid': 'wechat-robot',
        }
        try:
            response = requests.post(api_url, data=data).json()
            # 字典的get方法在字典没有'text'值的时候会返回None而不会抛出异常
            return response.get('text')
        # 为了防止服务器没有正常响应导致程序异常退出，这里用try-except捕获了异常
        # 如果服务器没能正常交互（返回非json或无法连接），那么就会进入下面的return
        except EXCEPTIONS:
            # 将会返回一个None
            return

    async def error_report(self, error, user=None, up_report=True):
        '错误处理, 向用户发送错误信息或继续上报错误'
        await self.logger.info(error)
        if up_report:
            raise NotImplementedError(error)
        else:
            self.send(str(error), user)

    def search_list(self, user_name=None):
        '在用户列表中查找当前用户是否已经绑定'
        if user_name is not None:
            user = Helper_user.objects.filter(robot=self.robot).filter(user_name=user_name)
            if user:
                return user[0]
            else:
                return self.add_user(user_name)
        else:
            return Helper_user.objects.filter(robot=self.robot)

    async def create_message(self, text, message_type,
                             name, user, send_user):
        '写入日志并保存消息'
        if user['NickName'] == send_user['NickName']:
            direction = 'IN'
            msg_pattern = '收到来自%s的消息: %s'
        else:
            direction = 'OUT'
            msg_pattern = '发出给%s的消息: %s'

        message = Message.objects.create(
            text=text,
            user=name,
            robot=self.robot,
            message_type=message_type,
            direction=direction
        )
        await self.logger.info(msg_pattern % (name, text))
        await message.send_to_client()

    async def send(self, text, user=None):
        '搜索用户并发送, 默认发给自己'
        def get_user_name(user):
            '自动处理  获取用户名'
            if isinstance(user, dict):
                if 'UserName' in user.keys():
                    return user['UserName']

            elif isinstance(user, Helper_user):
                return user.wx_UserName

            elif isinstance(user, str):
                if '@' in user:
                    return user
                else:
                    if itchat.search_friends(nickName=user):
                        return itchat.search_friends(nickName=user)[0]['UserName']
                    elif itchat.search_friends(name=user):
                        return itchat.search_friends(name=user)[0]['UserName']
            else:
                return None

        # send函数主体
        try:
            send_user = {'NickName': self.robot.nick_name}
            user_name = get_user_name(user)
            user = itchat.search_friends(userName=user_name)
            name = user['RemarkName'] if user['RemarkName'] else user['NickName']
            itchat.send(text, user_name)
            await self.create_message(text, itchat.content.TEXT,
                                      name, user, send_user)
        except EXCEPTIONS as error:
            await self.logger.info(error)

    def wxname_update(self):
        '更新用户名, 在登陆时调用'
        for user in self.search_list():
            user.wx_UserName = itchat.search_friends(
                remarkName=user.user_name)[0]['UserName']
            user.save()

    def add_user(self, user_name):
        user = Helper_user(
            user_name=user_name,
            user_id='',
            password=''
        )
        user.save()
        return user

    def del_user(self, user_name):
        '删除用户'
        user = self.search_list(user_name=user_name)
        user.delete()

    def logout(self):
        '退出登陆'
        self.settings = Setting(self)
        self.IS_LOGIN = False
        self.robot = None
        itchat.logout()
        if os.path.exists(HELPER_PKL):
            os.remove(HELPER_PKL)


class Setting:
    '小助手设置'
    trans_dict = dict(
        ROBOT_REPLY='智能回复开关',
        VOICE_REPLY='语音回复开关',
    )

    def __init__(self, helper):
        '设置参数初始化'
        self.helper = helper
        self.ROBOT_REPLY = True
        self.VOICE_REPLY = True

    def __str__(self):
        settings = vars(self)
        del settings['helper']
        return str(settings)

    async def change_settings(self, items):
        self.VOICE_REPLY = items['VOICE_REPLY']
        self.ROBOT_REPLY = items['ROBOT_REPLY']
        await self.helper.logger.info('修改设置成功')



HELPER = Helper()
