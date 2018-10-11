'默认初始页面视图'
from django.shortcuts import render


def hello(request):
    url_list = [
        {'text': '博客', 'url': 'blog'},
        {'text': '小助手', 'url': 'helper'},
        {'text': '文件管理', 'url': 'file'},
        {'text': 'VNC', 'url': 'vnc'},
        {'text': 'Admin', 'url': 'admin'},
        {'text': '路由', 'url': 'cgi-bin/luci'},
        {'text': 'Syncthing', 'url': 'syncthing'}
    ]
    return render(request, 'index.html', dict(url_list=url_list))
