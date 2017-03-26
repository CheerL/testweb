import os
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .ucas.login import login as LG
from .ucas.main import HELPER
from .ucas import info, EXCEPTIONS, QR_pic, WX_pic

MSG_init = '请点击登录按钮'
MSG_error = '错误,请重新登录'
MSG_login = '小助手运行中'
MSG_scan = '请扫码二维码'
MSG_logout = '小助手成功退出'
MSG_reload = '重新启动'
MSG_remind = '小助手提醒中'

ITEM_LIST = [
    {'text':'登录', 'id':'login'},
    {'text':'聊天', 'id':'chat'},
    {'text':'日志', 'id':'log'},
    {'text':'设置', 'id':'setting'},
]
# Create your views here.

def index(request):
    'app初始界面, 有可能是唯一的界面'
    HELPER.host = request.get_host()
    print(HELPER.host)
    if HELPER.is_login:
        return run_page(request)
    else:
        return login_page(request)

def run_page(request):
    res = dict(
        status=HELPER.is_login,
        item_list=ITEM_LIST,
        page='login'
    )
    return render(request, 'app/run.html', res)

def login_page(request):
    status = HELPER.is_login
    msg = MSG_login if status else MSG_init
    res = dict(
        status=status,
        msg=msg,
        pic=WX_pic
    )
    return render(request, 'app/login.html', res)

def login(request, uuid=None):
    '终于登录了'
    try:
        if not uuid:
            inf, uuid = LG(QR_pic, 0)
            (msg, pic) = (MSG_scan, QR_pic) if inf == 'uuid' else (MSG_login, WX_pic)
            return JsonResponse(dict(
                status=True,
                inf=inf,
                uuid=uuid,
                msg=msg,
                pic=pic
            ))
        else:
            (status, msg) = (True, MSG_login) if LG(QR_pic, 1, uuid) else (False, MSG_error)
            return JsonResponse(dict(
                status=status,
                msg=msg,
                pic=WX_pic
            ))
    except EXCEPTIONS as error:
        info(error)
        HELPER.__init__()
        if os.path.isfile(QR_pic):
            os.remove(QR_pic)
        return JsonResponse(dict(
            status=False,
            msg=MSG_error,
            pic=WX_pic
        ))

def logout(request):
    '退出登录'
    HELPER.logout()
    return info_and_response(MSG_logout)

def remind(request):
    '提醒'
    HELPER.remind()
    return info_and_response(MSG_remind)

def setting(request):
    return render(request, 'app/setting.html')
def log(request):
    return render(request, 'app/log.html')
def chat(request):
    return render(request, 'app/chat.html')

def info_and_response(msg):
    '返回HTTP相应, 并输出日志'
    info(msg)
    return HttpResponse(msg)
