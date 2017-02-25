import os
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage, DefaultStorage
from PIL import Image
from .models import Photo
import django


pic_name = 'images/about-image.jpg'

# Create your views here.
def index(request):
    #pic = Photo()
    text = os.getcwd()
    result = {
        'title':'微信小助手',
        'body':text,
        'pic':pic_name
    }
    return render(request, 'app/index.html', result)

def draw():
    width = 100
    height = 100
    image = Image.new('RGB', (width, height), (155, 155, 155))
    image.save(pic_name, 'jpeg')

def main():
    draw()

if __name__ == '__main__':
    main()
    