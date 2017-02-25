import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from PIL import Image
import itchat


pic_name = 'QR.jpg'

# Create your views here.
def index(request):
    #pic = Photo()
    text = '微信小助手'
    result = {
        'title':text,
        'body':text,
        'pic':pic_name
    }
    return render(request, 'app/index.html', result)

def button(request):
    itchat.auto_login(picDir='static' + pic_name, hotReload=True)
    friend = itchat.search_mps(name='微信支付')[0]
    itchat.send('2333', friend['UserName'])
    itchat.run()
    itchat.send('2333', friend['UserName'])
    #页面重定向
    return HttpResponseRedirect('.')
    