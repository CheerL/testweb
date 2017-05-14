from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.template import RequestContext
from django import forms
from .models import User
# Create your views here.


# 表单
class UserForm(forms.Form):
    username = forms.CharField(label='用户', max_length=100)
    password = forms.CharField(label='密码', widget=forms.PasswordInput())
    # password = forms.CharField(label='密码', max_length=100)


# 登陆
@csrf_exempt
def login(request):
    if request.method == 'GET':
        info = ''
        username = request.COOKIES.get('username', '')
        password = request.COOKIES.get('password', '')
        if username and password:
            uf = UserForm(dict(username=username, password=password))
        else:
            uf = UserForm()

    elif request.method == 'POST':
        info = "用户名或密码错误"
        uf = UserForm(request.POST)

    if uf.is_valid():
        # 获取表单用户密码
        username = uf.cleaned_data['username']
        password = uf.cleaned_data['password']
        # 获取的表单数据与数据库进行比较
        user = User.objects.filter(
            username__exact=username, password__exact=password)
        if user:
            url = '/gateone/?ssh=ssh://%s@inner.cheerl.online/' % username
            response = HttpResponseRedirect(url)
            response.set_cookie('username', username, 24 * 60 * 60)
            response.set_cookie('password', password, 24 * 60 * 60)
            # return render(request, 'ssh/login.html', {'uf': uf, 'info':
            # info})
            return render(request, 'ssh/main.html', {'user': username})

    return render(request, 'ssh/login.html', {'uf': uf, 'info': info})


# 退出
def logout(request):
    response = HttpResponseRedirect('/ssh/')
    response.delete_cookie('username')
    response.delete_cookie('password')
    return response
