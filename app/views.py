import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from PIL import Image
import itchat


pic_name = 'pic.jpg'
QR_name = 'QR.jpg'

# Create your views here.
def index(request):
    #pic = Photo()
    if os.path.isfile('static' + pic_name):
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
    itchat.auto_login(picDir='static' + pic_name, hotReload=True)
    friend = itchat.search_mps(name='微信支付')[0]
    itchat.send('2333', friend['UserName'])
    draw()
    #页面重定向
    return HttpResponseRedirect('.')

def draw():
    from random import randint
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), (randint(0, 255), randint(0, 255), randint(0, 255)))
    image.save('static/' + pic_name, 'jpeg')
    