'程序运行主体'
import re
import time
import requests
import itchat
from . import EXCEPTIONS, info
from . import helper as hp, TIMEOUT
from .helper import Helper
from .wheel import parallel as pl
#from .wheel.recognize import spech_recognize

HELPER = Helper()
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
        if HELPER.admin_report:
            pass
        if '?data?' in text:
            return '@fil@static/data.csv'
        elif '?robot?' in text:
            HELPER.robot_reply = bool(1 - HELPER.robot_reply)
            return '机器人回复已经%s' % ('打开' if HELPER.robot_reply else '关闭')
        elif '?log?' in text:
            return '@fil@static/run.log'
        elif '?update?' in text:
            HELPER.remind_list_update()
            HELPER.save_user_list()
            return '所有用户信息更新成功'
        elif '?kill?' in text:
            tid = int(re.findall(r'(\d+)', text)[0])
            pl.kill_thread(tid=tid)
            return '已经关闭线程%d' % tid
        elif '?remind?' in text:
            if HELPER.remind_alive:
                HELPER.remind_alive = False
            else:
                HELPER.remind_alive = True
                HELPER.remind()
            return 'remind_alive已经%s' % ('打开' if HELPER.remind_alive else '关闭')
        elif '?save?' in text:
            HELPER.save_user_list()
            return '保存成功'
        elif '?status?' in text:
            return 'remind_alive:%s\nrobot_reply:%s\nlast_update:%d mins ago\
            \nREMIND_WAIT:%s mins\nREMIND_BEFORE:%s mins\nAUTO_UPDATE:%s mins' % \
                (
                    '打开' if HELPER.remind_alive else '关闭',
                    '打开' if HELPER.robot_reply else '关闭',
                    (time.time()-HELPER.last_update)/60,
                    hp.REMIND_WAIT, hp.REMIND_BEFORE, hp.AUTO_UPDATE
                    )
        elif '?remind wait?' in text:
            hp.REMIND_WAIT = float(re.findall(r'(\d+\.?\d*)', text)[0])
            return 'REMIND_WAIT改为%f分钟' % hp.REMIND_WAIT
        elif '?remind before?' in text:
            hp.REMIND_BEFORE = float(re.findall(r'(\d+\.?\d*)', text)[0])
            return 'REMIND_BEFORE改为%f分钟' % hp.REMIND_BEFORE
        elif '?course dict?' in text:
            result = re.findall(r'(\d+):(\d+):(\d+)', text)[0]
            hp.COURSE_DICT[result[0]] = [int(result[1]), int(result[2])]
            return "COURSE_DICT['%d']改为(%d, %d)" % result
        elif '?send?' in text:
            result = re.findall(r'用户[:：\s]*(.+?)\s*内容[:：\s]*(.*)$', text)
            if result[0][0] == 'all':
                for user in HELPER.user_list:
                    HELPER.send(result[0][1], user['nick_name'])
            else:
                HELPER.send(result[0][1], result[0][0])
            return '发送成功'
        elif '?user?' in text:
            return ', '.join([user['nick_name'] for user in HELPER.user_list])
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
            HELPER.help(now_user, [keys_2, keys_1, keys_3[:1]])
        elif '文字课表' in text:
            HELPER.show_course_list(now_user, nick_name, False)
        elif '编号' in text:
            HELPER.show_course_list(now_user, nick_name, False, is_with_num=True)
        elif '保存' in text:
            HELPER.save_user_list(now_user)
        elif '退课' in text:
            HELPER.drop_course(now_user, nick_name, text)
        elif '选课' in text:
            HELPER.add_course(now_user, nick_name, text)
        elif '刷新' in text:
            HELPER.remind_list_update(nick_name)
            HELPER.save_user_list()
            return '个人信息刷新成功'
        elif '提醒' in text:
            HELPER.show_remind_list(now_user, nick_name)
        elif '课表' in text:
            HELPER.show_course_list(now_user, nick_name)
            return '若课表不正确, 可以试着回复"刷新"来刷新课程信息'
        elif '绑定' in text:
            HELPER.add_user(now_user, nick_name, text)
        else:
            if HELPER.robot_reply:
                return Helper.get_response(text)
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
'''
@itchat.msg_register(['Recording', 'Attachment', 'Video'])
def download_files(msg):
    '接收语音'
    voice_path = 'static/' + msg['FileName']
    msg['Text'](voice_path)
    #return spech_recognize(voice_path)
    
    itchat.send(
        '@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', voice_name),
        msg['FromUserName']
        )
    '''
    #msg['Text'] = ''
    #msg['MsgType'] = 'Text'
    #return

def main():
    '开始运行'
    requests.get('http://%s/app/remind' % HELPER.host, timeout=TIMEOUT)
    HELPER.is_run = True
    count = 0
    while HELPER.is_run:
        try:
            itchat.run()
            time.sleep(1)
            info(count)
        except EXCEPTIONS as error:
            if count < 5:
                count += 1
            else:
                HELPER.logout()
                info(error)

if __name__ == '__main__':
    try:
        main()
    except EXCEPTIONS as error:
        HELPER.my_error(error)
        HELPER.save_user_list()
