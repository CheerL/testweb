import os
import time
from django.shortcuts import render
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from PIL import Image
import itchat


pic_name = 'pic.jpg'
QR_name = 'QR.png'
COUNT = 0

# Create your views here.
def index(request):
    #pic = Photo()
    if os.path.isfile('static' + QR_name):
        text = '请扫码登陆'
    else:
        text = None
    result = {
        'title':'微信小助手',
        'body':text or '微信小助手',
        'pic':pic_name,
        'QR':QR_name,
    }
    return render(request, 'app/index.html', result)

def login(request):
    return HttpResponse(draw())

def draw():
    from random import randint
    global COUNT
    os.remove('static/' + str(COUNT) + pic_name)
    COUNT += 1
    width = 100
    height = 100
    name = 'static/' + str(COUNT) + pic_name
    image = Image.new('RGB', (width, height), (randint(0, 255), randint(0, 255), randint(0, 255)))
    image.save(name, 'jpeg')
    return '/' + name
    