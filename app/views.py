import os
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.files.storage import FileSystemStorage, DefaultStorage
from PIL import Image
from .models import Photo
import django


pic_name = '2333.jpg'

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
    from random import randint
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), (randint(0, 255), randint(0, 255), randint(0, 255)))
    image.save('static/' + pic_name, 'jpeg')
    #页面重定向
    return HttpResponseRedirect('.')
    