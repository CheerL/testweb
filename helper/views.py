import os
import json
import itchat
from ast import literal_eval
from channels import Group
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .wheel import parallel as pl
from .main import HELPER
from .base import info, EXCEPTIONS, QR_pic, WX_pic, log_read, pkl_path
from . import tests

MSG_init = '请点击登录按钮'
MSG_error = '错误,请重新登录'
MSG_login = '小助手运行中'
MSG_scan = '请扫描二维码'
MSG_logout = '小助手成功退出'
MSG_reload = '重新启动'
MSG_remind = '小助手提醒中'

ITEM_LIST = [
    {'text': '登录', 'id': 'login'},
    {'text': '聊天', 'id': 'chat'},
    {'text': '日志', 'id': 'log'},
    {'text': '设置', 'id': 'setting'},
]

# Create your views here.


def index(request):
    'app初始界面, 有可能是唯一的界面'
    if HELPER.IS_LOGIN:
        return run_page(request)
    else:
        return login_page(request)
# 跳转页面部分


def run_page(request):
    res = dict(
        status=HELPER.IS_LOGIN,
        item_list=ITEM_LIST,
        page='login'
    )
    return render(request, 'helper/run.html', res)


def login_page(request):
    status = HELPER.IS_LOGIN
    msg = MSG_login if status else MSG_init
    res = dict(
        status=status,
        msg=msg,
        pic=WX_pic
    )
    return render(request, 'helper/login.html', res)


def log_page(request):
    return render(request, 'helper/log.html')


def chat_page(request):
    return render(request, 'helper/chat.html')


def setting_page(request):
    item_list = vars(HELPER.settings).items()
    bool_list = [
        {
            'name': name,
            'show': HELPER.settings.trans_to_chinese(name),
            'val': val
        }
        for name, val in item_list if isinstance(val, bool)
    ]
    num_list = [
        {
            'name': name,
            'show': HELPER.settings.trans_to_chinese(name),
            'val': val if name != 'FLEXIBLE_DAY' else HELPER.settings.trans_flexible_day()
        }
        for name, val in item_list if not isinstance(val, bool) and name != 'LAST_UPDATE'
    ]
    show_list = []
    return render(
        request,
        'helper/setting.html',
        {'bool_list': bool_list, 'num_list': num_list, 'show_list': show_list}
    )

# 登陆 api


def login(request, uuid=None):
    '终于登录了'
    def qr_func(uuid, status, qrcode):
        info('成功获取二维码')
        with open(QR_pic, 'wb') as pic:
            pic.write(qrcode)
        Group('login').send({'text': json.dumps(dict(
            msg=MSG_scan,
            pic=QR_pic
        ))})

    def login_func():
        user = itchat.search_friends()
        info('%s成功登录' % user['NickName'])
        HELPER.wxname_update()
        HELPER.remind()
        HELPER.IS_LOGIN = True
        if os.path.exists(QR_pic):
            os.remove(QR_pic)
        Group('login').send({'text': json.dumps(dict(
            msg=MSG_login,
            pic=WX_pic
        ))})

    def exit_func():
        HELPER.logout()
        info(MSG_logout)

    def login_main():
        try:
            info('尝试登陆')
            itchat.auto_login(True, pkl_path, False, QR_pic,
                              qr_func, login_func, exit_func)
            itchat.run(debug=True, blockThread=False)
        except:
            Group('login').send({'text': json.dumps(dict(
                msg=MSG_error,
                pic=WX_pic
            ))})

    pl.run_thread([(login_main, ())], is_lock=False)
    return HttpResponse()


def logout(request):
    '退出登录'
    HELPER.logout()
    info(MSG_logout)
    return HttpResponse(MSG_logout)


# 日志 api
def get_log(request, start=0, count=1):
    log_list = log_read(count=int(count), start=int(start))
    return JsonResponse(dict(log_list=log_list))


def get_log_all(request):
    log_list = log_read(count=-1, start=0)
    return HttpResponse('<br>'.join(log_list))


@csrf_exempt
def send_log(request):
    if request.method == 'POST':
        Group('log').send({'text': json.dumps({"msg": request.POST['msg']})})
    return HttpResponse()


# 聊天 api
def get_chat_user(request):
    user_list = itchat.get_friends()
    for user in user_list:
        HELPER.get_head_img(user)
    return JsonResponse(dict(user_list=user_list, count=len(user_list)))


@csrf_exempt
def chat_send(request):
    '主动发送消息'
    try:
        if request.method == 'POST':
            msg = request.POST['msg']
            user = request.POST['user']
            HELPER.send(msg, user)
            return JsonResponse(dict(res=True))
        else:
            raise NotImplementedError('访问错误')
    except EXCEPTIONS as error:
        return JsonResponse(dict(res=False, msg=error))


# 设置api
@csrf_exempt
def setting_change(request):
    if request.method == 'POST':
        items = literal_eval(request.POST['res'])
        for day in ['一', '二', '三', '四', '五', '六', '日', '天']:
            if day in items['FLEXIBLE_DAY']:
                if day == '天':
                    items['FLEXIBLE_DAY'] = '星期日'
                else:
                    items['FLEXIBLE_DAY'] = '星期' + day
                break
        else:
            return JsonResponse({'res': True, 'msg': '灵活调整日期有误'})

        HELPER.settings.VOICE_REPLY = items['VOICE_REPLY']
        HELPER.settings.UPDATE_WAIT = items['UPDATE_WAIT']
        HELPER.settings.REMIND_ALIVE = items['REMIND_ALIVE']
        HELPER.settings.REMIND_BEFORE = items['REMIND_BEFORE']
        HELPER.settings.REMIND_WAIT = items['REMIND_WAIT']
        HELPER.settings.ROBOT_REPLY = items['ROBOT_REPLY']
        HELPER.settings.FLEXIBLE = items['FLEXIBLE']
        HELPER.settings.trans_flexible_day(items['FLEXIBLE_DAY'])
        HELPER.settings.remind_change()
        info("修改设置 %s" % items)
        return JsonResponse({'res': True, 'msg': '修改成功\n' + str(HELPER.settings)})
    else:
        return JsonResponse({'res': False, 'msg': '访问错误'})


# send测试关闭
# def send_page(request):
#     return render(request, 'helper/send.html')


# def send_to_channel(request, content=None, channel=None):
#     Group(channel).send({'text': json.dumps({"msg": content})})
#     return HttpResponse('send %s to %s' % (content, channel))


# def send_login(request):
#     tests.lll()
#     return HttpResponse()
# end
