import os
from logging import getLogger
from django.shortcuts import render
from django.http import HttpResponse
from app.login import login as LG
from app.helper.ucas import EXCEPTIONS
from app.login import PKL
import itchat


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
    global LIMIT, LOGIN
    #global f
    if LIMIT >= 2:
        LOGIN = LG(QR_name)
        LIMIT = 0
    LIMIT += 1
    try:
        return HttpResponse(next(LOGIN))
    except EXCEPTIONS as error:
        LIMIT = 0
        if os.path.isfile(PKL):
            os.remove(PKL)
        #logger.info(error)
        raise ConnectionError(error)
        return HttpResponse(error)

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
