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
@async_to_sync
# @async_utils.async_wrap()
async def add_friend(msg):
    '自动接受好友申请'
    itchat.add_friend(**msg['Text'])
    user = msg['Text']['autoUpdate']
    await HELPER.send('Nice to see you! 你可以试着输入"???"来查看帮助信息', user['UserName'])
    await HELPER.logger.info('添加新好友%s' % (user['NickName']))


@itchat.msg_register([itchat.content.TEXT, itchat.content.VOICE])
@async_to_sync
# @async_utils.async_wrap()
async def reply(msg):
    try:
        message_type = msg['Type']
        send_user = itchat.search_friends(userName=msg['FromUserName'])
        user = msg['User']
        name = user['RemarkName'] if user['RemarkName'] else user['NickName']
        if message_type == itchat.content.TEXT:
            await text_reply(msg['Text'], message_type, name, user, send_user)
        elif message_type == itchat.content.VOICE:
            await voice_reply(msg['FileName'], message_type, name, user, send_user)

    except EXCEPTIONS as error:
        await HELPER.error_report(error, msg['FromUserName'], False)

async def text_reply(text, message_type, name, user, send_user):
    '文字消息的回复'
    await HELPER.create_message(text, message_type,
                                name, user, send_user)

    if '???' in text or '？？？' in text:
        msg = '功能有: ' + ', '.join([', '.join(each) for each in [KEYS_1[:1]]])
        await HELPER.send(msg, send_user)
    else:
        if HELPER.settings.ROBOT_REPLY:
            await HELPER.send(HELPER.get_robot_response(text), send_user)


async def voice_reply(file_name, message_type, name, user, send_user):
    '语音消息的回复'
    voice_path = 'media/voices/%s' % file_name
    await HELPER.create_message('语音' + voice_path, message_type,
                                name, send_user, user)

    if HELPER.settings.VOICE_REPLY:
        translate = recognize.spech_recognize(voice_path)
        if translate:
            await HELPER.send('你说的是:' + translate, send_user)
            await HELPER.logger.info('收到来自%s的语音, 内容: %s' % (name, translate))
            await text_reply(translate, itchat.content.TEXT,
                             name, user, send_user)
        else:
            await HELPER.send('我没有听懂', send_user)
