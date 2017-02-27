'程序运行主体'
import re
import itchat
from . import helper as hp
from .helper import Helper
from .SEP import EXCEPTIONS
from .login import login

HELPER = Helper()
ADMIN_HELP = '''?data.csv?   None
?remind alive?  None
?user?          None
?save time?     \\f
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
        keys_2 = ['绑定', '退课', '选课', '更新', '保存', '提醒', '课表']
        keys_3 = ['???', '？？？']
        if '?data.csv?' in text:
            return '@fil@static/data.csv'
        elif '?remind alive?' in text:
            if HELPER.remind_alive:
                HELPER.remind_alive = False
            else:
                HELPER.remind_alive = True
                HELPER.remind()
            return 'remind_alive已更改'
        elif '?save time?' in text:
            hp.SAVE_TIME = float(re.findall(r'(\d+\.?\d*)', text)[0])
            return 'SAVE_TIME改为%f分钟' % hp.SAVE_TIME
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
            HELPER.send(result[0][1], result[0][0])
            return '发送成功'
        elif '?user?' in text:
            return ', '.join([user['nick_name'] for user in HELPER.user_list])
        elif '?admin?' in text:
            return ADMIN_HELP
            HELPER.admins = nick_name
        elif '重新绑定' in text:
            HELPER.change_user(now_user, nick_name, text)
        elif '取消绑定' in text:
            HELPER.del_user(now_user, nick_name)
        elif '取消提醒' in text:
            HELPER.cancel_remind(now_user, nick_name)
        elif '打开提醒' in text:
            HELPER.remind(now_user, nick_name)
        elif '???' in text:
            HELPER.help(now_user, [keys_2, keys_1, keys_3[:1]])
        elif '？？？' in text:
            HELPER.help(now_user, [keys_2, keys_1, keys_3[:1]])
        elif '文字课表' in text:
            if '编号' in text:
                HELPER.show_course_list(now_user, nick_name, False, is_with_num=True)
            else:
                HELPER.show_course_list(now_user, nick_name, False)
        elif '保存' in text and '成功' not in text:
            HELPER.save_user_list(now_user)
        elif '退课' in text:
            HELPER.drop_course(now_user, nick_name, text)
        elif '选课' in text:
            HELPER.add_course(now_user, nick_name, text)
        elif '更新' in text:
            HELPER.remind_list_update(now_user, nick_name)
        elif '提醒' in text:
            HELPER.show_remind_list(now_user, nick_name)
        elif '课表' in text:
            HELPER.show_course_list(now_user, nick_name)
            #return "课表功能暂时失效, 请使用文字课表功能"
        elif '绑定' in text:
            HELPER.add_user(now_user, nick_name, text)
        else:
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
    return 'Nice to see you!\n你可以试着输入"???"来查看帮助信息'

@itchat.msg_register(itchat.content.RECORDING)
def download_files(msg):
    '接收语音'
    voice_name = 'static/' + msg['FileName']
    msg['Text'](voice_name)
    itchat.send(
        '@%s@%s'%('img' if msg['Type'] == 'Picture' else 'fil', voice_name),
        msg['FromUserName']
        )
    #msg['Text'] = ''
    #msg['MsgType'] = 'Text'
    return

def main():
    '开始运行'
    HELPER.remind()
    HELPER.auto_save()
    itchat.run()

if __name__ == '__main__':
    try:
        main()
    except EXCEPTIONS as error:
        HELPER.my_error(error)
        HELPER.save_user_list()
