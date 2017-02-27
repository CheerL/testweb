from logging import getLogger
from django.shortcuts import render
from django.http import HttpResponse
from .ucas.wheel import parallel as pl
from .ucas.login import login as LG
from .ucas import EXCEPTIONS, main

QR_name = 'static/QR.png'
COUNT = 0
LIMIT = 0
LOGIN = LG(QR_name)
logger = getLogger('helper')

# Create your views here.
def index(request):
    'app初始界面, 有可能是唯一的界面'
    global LIMIT, LOGIN
    LIMIT = 0
    LOGIN = LG(QR_name)
    return render(request, 'app/index.html', None)

def login(request):
    '终于登陆了'
    if not request:
        return no_request()
    try:
        global LIMIT, LOGIN
        #global f
        if LIMIT >= 2:
            LOGIN = LG(QR_name)
            LIMIT = 0
        LIMIT += 1
        response = next(LOGIN)
        return HttpResponse(response)
    except EXCEPTIONS:
        LIMIT = 0
        LOGIN = LG(QR_name)
        logger.info('登陆错误')
        return HttpResponse("错误, 请重新登陆")

def run(request):
    '开始执行'
    if not request:
        return no_request()
    try:
        global LIMIT, LOGIN
        main.HELPER.host = request.get_host()
        pl.run_thread([(main.main, ())], None, False)
        return HttpResponse('开始执行程序')
    except EXCEPTIONS:
        LIMIT = 0
        LOGIN = LG(QR_name)
        return HttpResponse("错误, 请重新登陆")

def logout(request):
    '退出登陆'
    if not request:
        return no_request()
    main.HELPER.logout()
    return HttpResponse('成功退出')

def save_all(request):
    '保存'
    if not request:
        return no_request()
    main.HELPER.auto_save()
    logger.info('成功储存所有用户信息')
    return HttpResponse('')

def remind(request):
    '提醒'
    if not request:
        return no_request()
    main.HELPER.remind()
    logger.info('提醒中')
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
    yield '/' + name
    time.sleep(5)
    if os.path.isfile(name):
        os.remove(name)
    yield
'''
