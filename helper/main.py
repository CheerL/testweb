'程序运行主体'
import re
import time

# from helper.async_itchat import async_itchat as itchat
import itchat
from asgiref.sync import async_to_sync
from helper.helper import HELPER
from helper.models import Message
from helper.setting import EXCEPTIONS
from helper.utils import async_utils, recognize

# ADMIN_HELP = '''?data?   None
# ?robot          None
# ?log?           None
# ?update?        None
# ?remind?        None
# ?status?        None
# ?user?          None
# ?remind wait?   \\f
# ?remind before? \\f
# ?course dict?   \\d:\\d:\\d
# ?send?          用户:\\s 内容:\\s'''

KEYS_1 = ['???', '？？？']


@itchat.msg_register(itchat.content.FRIENDS)
# @async_to_sync
@async_utils.async_wrap()
async def add_friend(msg):
    '自动接受好友申请'
    itchat.add_friend(**msg['Text'])
    user = msg['Text']['autoUpdate']
    await HELPER.send('Nice to see you! 你可以试着输入"???"来查看帮助信息', user['UserName'])
    await HELPER.logger.info('添加新好友%s' % (user['NickName']))


@itchat.msg_register([itchat.content.TEXT, itchat.content.VOICE])
# @async_to_sync
@async_utils.async_wrap()
async def reply(msg):
    try:
        text = msg['Text']
        message_type = msg['Type']
        send_user_name = msg['FromUserName']
        send_user = itchat.search_friends(userName=send_user_name)
        user = msg['User']
        alias = user['RemarkName']
        nick_name = user['NickName']
        name = alias if alias else nick_name

        if message_type == itchat.content.TEXT:
            await text_reply(msg, text, send_user_name, message_type,
                       send_user, user, alias, name)
        elif message_type == itchat.content.VOICE:
            await voice_reply(msg, text, send_user_name, message_type,
                        send_user, user, alias, name)

    except EXCEPTIONS as error:
        await HELPER.logger.error_report(error, send_user_name, False)


async def info_save_message(text, message_type, send_user, user, name, info_text):
    '写入日志并保存消息'
    if user['NickName'] == send_user['NickName']:
        await HELPER.logger.info('收到来自' + info_text)
        message = Message.objects.create(
            text=text, user=name, robot=HELPER.robot,
            message_type=message_type, direction='IN'
        )
    else:
        await HELPER.logger.info('发出给' + info_text)
        message = Message.objects.create(
            text=text, user=name, robot=HELPER.robot,
            message_type=message_type, direction='OUT'
        )
    await message.send_to_client()


async def text_reply(msg, text, send_user_name, message_type, send_user, user, alias, name):
    '文字消息的回复'
    info_text = '%s的消息: %s' % (name, text)
    await info_save_message(text, message_type, send_user, user, name, info_text)

    if '???' in text or '？？？' in text:
        msg = '功能有: ' + ', '.join([', '.join(each) for each in [KEYS_1[:1]]])
        await HELPER.send(msg, send_user_name)
    else:
        if HELPER.settings.ROBOT_REPLY:
            await HELPER.send(HELPER.get_robot_response(text), send_user_name)


async def voice_reply(msg, text, send_user_name, message_type, send_user, user, alias, name):
    '语音消息的回复'
    voice_path = 'static/voices/%s' % (msg['FileName'])

    info_text = '%s的语音' % (name)
    await info_save_message(str(voice_path), message_type,
                      send_user, user, name, info_text)

    if HELPER.settings.VOICE_REPLY:
        translate = recognize.spech_recognize(voice_path)
        if translate:
            await HELPER.send('你说的是:' + translate, send_user_name)
            await HELPER.logger.info('收到来自%s的语音的内容: %s' % (name, translate))
            msg['Text'] = translate
            msg['Type'] = itchat.content.TEXT
            reply(msg)
        else:
            await HELPER.send('我没有听懂', send_user_name)
