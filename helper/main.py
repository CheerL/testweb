'程序运行主体'
import re
import time
import itchat
from .base import EXCEPTIONS, info, HELPER, error_report
from .wheel import parallel as pl
from .wheel.recognize import spech_recognize

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


def reply(msg):
    '回复函数'
    try:
        now_user = msg['FromUserName']
        text = msg['Text']
        user = itchat.search_friends(userName=now_user)
        alias = user['RemerkName']
        keys_1 = ['重新绑定', '取消绑定', '取消提醒', '打开提醒', '文字课表']
        keys_2 = ['绑定', '刷新', '提醒', '课表']
        keys_3 = ['???', '？？？']
        info('收到来自%s的消息: %s' % (user['NickName'], text))

        # 采用新方式实现管理员功能
        # if '?data?' in text:
        #     return '@fil@static/data.csv'
        # elif '?robot?' in text:
        #     HELPER.settings.ROBOT_REPLY = bool(1 - HELPER.settings.ROBOT_REPLY)
        #     return '机器人回复已经%s' % ('打开' if HELPER.settings.ROBOT_REPLY else '关闭')
        # elif '?log?' in text:
        #     return '@fil@static/run.log'
        # elif '?update?' in text:
        #     HELPER.remind_list_update()
        #     return '所有用户信息更新成功'
        # elif '?kill?' in text:
        #     tid = int(re.findall(r'(\d+)', text)[0])
        #     pl.kill_thread(tid=tid)
        #     return '已经关闭线程%d' % tid
        # elif '?remind?' in text:
        #     if HELPER.settings.REMIND_ALIVE:
        #         HELPER.settings.REMIND_ALIVE = False
        #     else:
        #         HELPER.settings.REMIND_ALIVE = True
        #         HELPER.remind()
        #     return 'remind_alive已经%s' % ('打开' if HELPER.settings.REMIND_ALIVE else '关闭')
        # elif '?status?' in text:
        #     return 'remind_alive:%s\nrobot_reply:%s\nlast_update:%d mins ago\
        #     \nREMIND_WAIT:%s mins\nREMIND_BEFORE:%s mins\nUPDATE_WAIT:%s mins' % \
        #         (
        #             '打开' if HELPER.settings.REMIND_ALIVE else '关闭',
        #             '打开' if HELPER.settings.ROBOT_REPLY else '关闭',
        #             (time.time()-HELPER.settings.LAST_UPDATE)/60,
        #             HELPER.settings.REMIND_WAIT,
        #             HELPER.settings.REMIND_BEFORE,
        #             HELPER.settings.UPDATE_WAIT
        #             )
        # elif '?remind wait?' in text:
        #     HELPER.settings.REMIND_WAIT = float(re.findall(r'(\d+\.?\d*)', text)[0])
        #     return 'REMIND_WAIT改为%f分钟' % HELPER.settings.REMIND_WAIT
        # elif '?remind before?' in text:
        #     HELPER.settings.REMIND_BEFORE = float(re.findall(r'(\d+\.?\d*)', text)[0])
        #     return 'REMIND_BEFORE改为%f分钟' % HELPER.settings.REMIND_BEFORE
        # elif '?admin?' in text:
        #     return ADMIN_HELP
        if '重新绑定' in text:
            HELPER.change_user(now_user, alias, text)
        elif '取消绑定' in text:
            HELPER.del_user(now_user, alias)
        elif '取消提醒' in text:
            HELPER.cancel_remind(now_user, alias)
        elif '打开提醒' in text:
            HELPER.remind(now_user, alias)
        elif '???' in text or '？？？' in text:
            HELPER.my_help(now_user, [keys_2, keys_1, keys_3[:1]])
        elif '文字课表' in text:
            HELPER.show_course_list(now_user, alias, False)
        elif '编号' in text:
            HELPER.show_course_list(
                now_user, alias, False, is_with_num=True)
        # 选退课功能关闭
            # elif '退课' in text:
            #     HELPER.drop_course(now_user, alias, text)
            # elif '选课' in text:
            #     HELPER.add_course(now_user, alias, text)
        elif '刷新' in text:
            HELPER.remind_list_update(alias)
            return '个人信息刷新成功'
        elif '提醒' in text:
            HELPER.show_remind_list(now_user, alias)
        elif '课表' in text:
            HELPER.show_course_list(now_user, alias)
        elif '绑定' in text:
            HELPER.add_user(now_user, alias, text)
        else:
            if HELPER.settings.ROBOT_REPLY:
                return HELPER.get_robot_response(text)
    except EXCEPTIONS as error:
        error_report(error, now_user, False)


@itchat.msg_register(itchat.content.TEXT)
def text_reply(msg):
    '回复文字'
    return reply(msg)


@itchat.msg_register(itchat.content.FRIENDS)
def add_friend(msg):
    '自动接受好友申请'
    itchat.add_friend(**msg['Text'])
    itchat.send('Nice to see you!\n你可以试着输入"???"来查看帮助信息',
                msg['Text']['userName'])


@itchat.msg_register(['Recording', 'Attachment', 'Video'])
def download_files(msg):
    '接收语音'
    if HELPER.settings.VOICE_REPLY:
        voice_path = 'static/voice/' + msg['FileName']
        msg['Text'](voice_path)
        now_user = msg['FromUserName']
        user = itchat.search_friends(userName=now_user)
        info('收到来自%s的语音' % (user['NickName']))
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
