'程序运行主体'
import re
import time
# from helper.async_itchat import async_itchat as itchat
import itchat
from helper.base import EXCEPTIONS, info, HELPER, error_report, itchat_send
from helper.utils import parallel as pl
from helper.utils.recognize import spech_recognize
from helper.models import Message

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

KEYS_1 = ['重新绑定', '取消绑定', '取消提醒', '打开提醒', '文字课表']
KEYS_2 = ['绑定', '刷新', '提醒', '课表']
KEYS_3 = ['???', '？？？']


@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    '自动接受好友申请'
    itchat.add_friend(**msg['Text'])
    user = msg['Text']['autoUpdate']
    itchat_send('Nice to see you! 你可以试着输入"???"来查看帮助信息', user['UserName'])
    info('添加新好友%s' % (user['NickName']))


@itchat.msg_register([itchat.content.TEXT, itchat.content.VOICE])
def reply(msg):
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
            text_reply(msg, text, send_user_name, message_type,
                       send_user, user, alias, name)
        elif message_type == itchat.content.VOICE:
            voice_reply(msg, text, send_user_name, message_type,
                        send_user, user, alias, name)

    except EXCEPTIONS as error:
        error_report(error, send_user_name, False)


def info_save_message(text, message_type, send_user, user, name, info_text):
    '写入日志并保存消息'
    if user['NickName'] == send_user['NickName']:
        info('收到来自' + info_text)
        message = Message.objects.create(
            text=text, user=name, robot=HELPER.robot,
            message_type=message_type, direction='IN'
        )
    else:
        info('发出给' + info_text)
        message = Message.objects.create(
            text=text, user=name, robot=HELPER.robot,
            message_type=message_type, direction='OUT'
        )
    message.send_to_client()


def text_reply(msg, text, send_user_name, message_type, send_user, user, alias, name):
    '文字消息的回复'
    info_text = '%s的消息: %s' % (name, text)
    info_save_message(text, message_type, send_user, user, name, info_text)

    if '重新绑定' in text:
        HELPER.change_user(send_user_name, alias, text)
    elif '取消绑定' in text:
        HELPER.del_user(send_user_name, alias)
    elif '取消提醒' in text:
        HELPER.cancel_remind(send_user_name, alias)
    elif '打开提醒' in text:
        HELPER.remind(send_user_name, alias)
    elif '???' in text or '？？？' in text:
        HELPER.my_help(send_user_name, [KEYS_2, KEYS_1, KEYS_3[:1]])
    elif '文字课表' in text:
        HELPER.show_course_list(send_user_name, alias, False)
    elif '编号' in text:
        HELPER.show_course_list(
            send_user_name, alias, False, is_with_num=True)
    # 选退课功能关闭
        # elif '退课' in text:
        #     HELPER.drop_course(send_user_name, alias, text)
        # elif '选课' in text:
        #     HELPER.add_course(send_user_name, alias, text)
    elif '刷新' in text:
        HELPER.remind_list_update(alias)
        return '个人信息刷新成功'
    elif '提醒' in text:
        HELPER.show_remind_list(send_user_name, alias)
    elif '课表' in text:
        HELPER.show_course_list(send_user_name, alias)
    elif '绑定' in text:
        HELPER.add_user(send_user_name, alias, text)
    else:
        if HELPER.settings.ROBOT_REPLY:
            itchat_send(HELPER.get_robot_response(text), send_user_name)


def voice_reply(msg, text, send_user_name, message_type, send_user, user, alias, name):
    '语音消息的回复'
    voice_path = 'static/voices/%s' % (msg['FileName'])
    text(voice_path)

    info_text = '%s的语音' % (name)
    info_save_message(str(voice_path), message_type,
                      send_user, user, name, info_text)

    if HELPER.settings.VOICE_REPLY:
        translate = spech_recognize(voice_path)
        if translate:
            itchat.send('你说的是:' + translate, send_user_name)
            info('收到来自%s的语音的内容: %s' % (name, translate))
            msg['Text'] = translate
            msg['Type'] = itchat.content.TEXT
            reply(msg)
        else:
            itchat_send('我没有听懂', send_user_name)
