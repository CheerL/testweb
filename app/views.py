import os
from django.shortcuts import render
from django.http import HttpResponse
from .ucas.wheel import parallel as pl
from .ucas.login import login as LG
from .ucas import EXCEPTIONS, main, info

QR_name = 'static/QR.png'
#COUNT = 0
LOGIN = LG(QR_name)

# Create your views here.
def index(request):
    'app初始界面, 有可能是唯一的界面'
    return render(request, 'app/index.html',
                  {'is_login':main.HELPER.is_login,
                   'is_run':main.HELPER.is_run,
                   'is_wait':main.HELPER.is_wait})

def login(request):
    '终于登陆了'
    if not request:
        return no_request()
    try:
        global LOGIN
        if not main.HELPER.is_login and not main.HELPER.is_wait:
            LOGIN = LG(QR_name)
        response = next(LOGIN)
        return HttpResponse(response)
    except EXCEPTIONS:
        info('登陆错误')
        main.HELPER.is_wait = False
        if os.path.isfile(QR_name):
            os.remove(QR_name)
        return HttpResponse("错误, 请重新登陆")

def run(request):
    '开始执行'
    if not request:
        return no_request()
    try:
        main.HELPER.host = request.get_host()
        pl.run_thread([(main.main, ())], None, False)
        main.HELPER.is_run = True
        return HttpResponse('正在运行')
    except EXCEPTIONS:
        main.HELPER.is_login = False
        info('运行失败, 重新登陆')
        return HttpResponse("错误, 请重新登陆")

def logout(request):
    '退出登陆'
    if not request:
        return no_request()
    main.HELPER.logout()
    info('成功退出')
    return HttpResponse('成功退出')

def remind(request):
    '提醒'
    if not request:
        return no_request()
    main.HELPER.remind()
    info('提醒中')
    return HttpResponse('')

def reload(requset):
    '重启'
    if not requset:
        return no_request()
    main.HELPER.is_login = False
    main.HELPER.is_run = False
    main.HELPER.is_wait = False
    main.HELPER.remind_alive = False
    global LOGIN
    LOGIN = LG(QR_name)
    return HttpResponse('')

def no_request():
    '请求不存在时'
    return HttpResponse('页面不存在')
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
