import os
#from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .ucas.login import login as LG
from .ucas.main import HELPER
from .ucas import info as info_func, EXCEPTIONS

QR_pic = 'static/QR.png'
WX_pic = 'static/images/begin.png'

MSG_init = '请点击登录按钮'
MSG_error = '错误,请重新登录'
MSG_login = '小助手运行中'
MSG_scan = '请扫码二维码'
MSG_logout = '成功退出'
MSG_reload = '重新启动'

# Create your views here.

def index(request):
    'app初始界面, 有可能是唯一的界面'
    HELPER.host = request.get_host()
    status = HELPER.is_login
    msg = MSG_login if status else MSG_init
    res = dict(
        status=status,
        msg=msg,
        pic=WX_pic
    )
    return render(request, 'app/index.html', res)

def login(request, uuid=None):
    '终于登录了'
    try:
        if not uuid:
            info, uuid = LG(QR_pic, 0)
            (msg, pic) = (MSG_scan, QR_pic) if info == 'uuid' else (MSG_login, WX_pic)
            return JsonResponse(dict(
                status=True,
                info=info,
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
    return info_and_response('提醒中')

def reload(requset):
    '重启'
    HELPER.logout()
    return info_and_response(MSG_reload)

def info_and_response(msg):
    '返回HTTP相应, 并输出日志'
    info_func(msg)
    return HttpResponse(msg)
