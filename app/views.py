import os
from logging import getLogger
import itchat
from django.shortcuts import render
from django.http import HttpResponse
from .ucas.wheel import parallel as pl
from .ucas.login import login as LG
from .ucas import main


QR_name = 'static/QR.png'
COUNT = 0
LIMIT = 0
LOGIN = LG(QR_name)
logger = getLogger('helper')

# Create your views here.
def index(request):
    'app初始界面, 有可能是唯一的界面'
    return render(request, 'app/index.html', None)

def login(request):
    '终于登陆了'
    try:
        if not request:
            raise NotImplementedError('请求不存在')
        global LIMIT, LOGIN
        #global f
        if LIMIT >= 2:
            LOGIN = LG(QR_name)
            LIMIT = 0
        LIMIT += 1
        return HttpResponse(next(LOGIN))
    except main.EXCEPTIONS:
        LIMIT = 0
        LOGIN = LG(QR_name)
        return HttpResponse("错误, 请重新登陆或退出")

def run(request):
    '开始执行'
    try:
        global LIMIT, LOGIN
        if not request:
            raise NotImplementedError('请求不存在')
        pl.run_thread([(main.main, ())], None, False)
        return HttpResponse('开始执行程序')
    except main.EXCEPTIONS:
        LIMIT = 0
        LOGIN = LG(QR_name)
        return HttpResponse("错误, 请重新登陆或退出")

def logout(request):
    itchat.logout()
    return HttpResponse('成功退出')
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
