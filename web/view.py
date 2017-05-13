'默认初始页面视图'
from django.http import HttpResponse
from django.shortcuts import render


def hello(request):
    url_list = [
        {'text': '小助手', 'url': 'helper'},
        {'text': '博客', 'url': 'blog'},
        {'text': '文件管理', 'url': 'file'},
        {'text': 'VNC', 'url': 'vnc'}
    ]
    return render(request, 'index.html', dict(url_list=url_list))
