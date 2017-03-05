import os
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .ucas.wheel import parallel as pl
from .ucas.login import login as LG
from .ucas import EXCEPTIONS, main, info
from .ucas.main import HELPER

QR_name = 'static/QR.png'

# Create your views here.
def index(request):
    'app初始界面, 有可能是唯一的界面'
    return render(request, 'app/index.html',
                  {'is_login':HELPER.is_login,
                   'is_run':HELPER.is_run,
                   'is_wait':HELPER.is_wait})

@csrf_exempt
def login(request):
    '终于登陆了'
    try:
        if request.method == 'POST':
            status = request.POST['status']
            uuid = request.POST['uuid'] or None
            return JsonResponse(LG(QR_name, status, uuid))
        raise NotImplementedError('访问错误')
    except EXCEPTIONS as error:
        info(error)
        HELPER.init()
        if os.path.isfile(QR_name):
            os.remove(QR_name)
        return JsonResponse({'res':'fail'})

def run(request):
    '开始执行'
    try:
        HELPER.host = request.get_host()
        pl.run_thread([(main.main, ())], None, False)
        HELPER.is_run = True
        return info_and_response('正在运行')

    except EXCEPTIONS:
        HELPER.is_login = False
        return info_and_response("错误, 请重新登陆")

def logout(request):
    '退出登陆'
    HELPER.logout()
    return info_and_response('成功退出')

def remind(request):
    '提醒'
    HELPER.remind()
    return info_and_response('提醒中')

def reload(requset):
    '重启'
    HELPER.logout()
    return info_and_response('重新启动')

def info_and_response(msg):
    '返回HTTP相应, 并输出日志'
    info(msg)
    return HttpResponse(msg)

'''
def draw():
    from random import randint
    global COUNT
    COUNT += 1
    width = 100
    height = 100
    name = 'static/' + str(COUNT) + pic_name
    image = Image.new('RGB', (width, height), (randint(0, 255), randint(0, 255), randint(0, 255)))
    image.save(name, 'jpeg')
'''
