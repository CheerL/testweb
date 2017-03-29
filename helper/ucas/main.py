'程序运行主体'
import re
import time
import itchat
from . import helper, EXCEPTIONS, info
from .wheel import parallel as pl
from .wheel.recognize import spech_recognize

HELPER = helper.Helper()
settings = HELPER.settings
ADMIN_HELP = '''?data?   None
?robot          None
?log?           None
?update?        None
?remind?        None
?status?        None
?user?          None
?remind wait?   \\f
?remind before? \\f
?course dict?   \\d:\\d:\\d
?send?          用户:\\s 内容:\\s'''

def reply(msg):
    '回复函数'
    try:
        now_user = msg['FromUserName']
        text = msg['Text']
        user = itchat.search_friends(userName=now_user)
        nick_name = user['NickName']
        keys_1 = ['重新绑定', '取消绑定', '取消提醒', '打开提醒', '文字课表']
        keys_2 = ['绑定', '退课', '选课', '刷新', '保存', '提醒', '课表']
        keys_3 = ['???', '？？？']
        info('收到来自%s的消息: %s' % (nick_name, text))
        if '?data?' in text:
            return '@fil@static/data.csv'
        elif '?robot?' in text:
            settings.ROBOT_REPLY = bool(1 - settings.ROBOT_REPLY)
            return '机器人回复已经%s' % ('打开' if settings.ROBOT_REPLY else '关闭')
        elif '?log?' in text:
            return '@fil@static/run.log'
        elif '?update?' in text:
            HELPER.remind_list_update()
            return '所有用户信息更新成功'
        elif '?kill?' in text:
            tid = int(re.findall(r'(\d+)', text)[0])
            pl.kill_thread(tid=tid)
            return '已经关闭线程%d' % tid
        elif '?remind?' in text:
            if settings.REMIND_ALIVE:
                settings.REMIND_ALIVE = False
            else:
                settings.REMIND_ALIVE = True
                HELPER.remind()
            return 'remind_alive已经%s' % ('打开' if settings.REMIND_ALIVE else '关闭')
        elif '?status?' in text:
            return 'remind_alive:%s\nrobot_reply:%s\nlast_update:%d mins ago\
            \nREMIND_WAIT:%s mins\nREMIND_BEFORE:%s mins\nUPDATE_WAIT:%s mins' % \
                (
                    '打开' if settings.REMIND_ALIVE else '关闭',
                    '打开' if settings.ROBOT_REPLY else '关闭',
                    (time.time()-settings.LAST_UPDATE)/60,
                    settings.REMIND_WAIT, settings.REMIND_BEFORE, settings.UPDATE_WAIT
                    )
        elif '?remind wait?' in text:
            settings.REMIND_WAIT = float(re.findall(r'(\d+\.?\d*)', text)[0])
            return 'REMIND_WAIT改为%f分钟' % settings.REMIND_WAIT
        elif '?remind before?' in text:
            settings.REMIND_BEFORE = float(re.findall(r'(\d+\.?\d*)', text)[0])
            return 'REMIND_BEFORE改为%f分钟' % settings.REMIND_BEFORE
        elif '?admin?' in text:
            return ADMIN_HELP
        elif '重新绑定' in text:
            HELPER.change_user(now_user, nick_name, text)
        elif '取消绑定' in text:
            HELPER.del_user(now_user, nick_name)
        elif '取消提醒' in text:
            HELPER.cancel_remind(now_user, nick_name)
        elif '打开提醒' in text:
            HELPER.remind(now_user, nick_name)
        elif '???' in text or '？？？' in text:
            HELPER.my_help(now_user, [keys_2, keys_1, keys_3[:1]])
        elif '文字课表' in text:
            HELPER.show_course_list(now_user, nick_name, False)
        elif '编号' in text:
            HELPER.show_course_list(now_user, nick_name, False, is_with_num=True)
        elif '退课' in text:
            HELPER.drop_course(now_user, nick_name, text)
        elif '选课' in text:
            HELPER.add_course(now_user, nick_name, text)
        elif '刷新' in text:
            HELPER.remind_list_update(nick_name)
            return '个人信息刷新成功'
        elif '提醒' in text:
            HELPER.show_remind_list(now_user, nick_name)
        elif '课表' in text:
            HELPER.show_course_list(now_user, nick_name)
            return '若课表不正确, 可以试着回复"刷新"来刷新课程信息'
        elif '绑定' in text:
            HELPER.add_user(now_user, nick_name, text)
        else:
            if settings.ROBOT_REPLY:
                return HELPER.get_response(text)
    except EXCEPTIONS as error:
        HELPER.my_error(error, now_user, False)

@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    '回复文字'
    return reply(msg)

@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    '自动接受好友申请'
    itchat.add_friend(**msg['Text'])
    itchat.send('Nice to see you!\n你可以试着输入"???"来查看帮助信息', msg['Text']['userName'])

@itchat.msg_register(['Recording', 'Attachment', 'Video'])
def download_files(msg):
    '接收语音'
    if settings.VOICE_REPLY:
        voice_path = 'static/' + msg['FileName']
        msg['Text'](voice_path)
        now_user = msg['FromUserName']
        user = itchat.search_friends(userName=now_user)
        nick_name = user['NickName']
        info('收到来自%s的语音' % (nick_name))
        translate = spech_recognize(voice_path)
        if translate:
            itchat.send('你说的是:' + translate, now_user)
            msg['Text'] = translate
            return reply(msg)
        else:
            return '我没有听懂'
    else:
        return '收到语音'
    # itchat.send(
    #     '@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', voice_name),
    #     msg['FromUserName']
    #     )
    # msg['Text'] = ''
    # msg['MsgType'] = 'Text'
    # return
