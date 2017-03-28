import os
import uuid
import json
import threading
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from dwebsocket.decorators import accept_websocket
from .ucas.login import login as LG
from .ucas.main import HELPER
from .ucas import info, EXCEPTIONS, QR_pic, WX_pic, log_read, send, clients

MSG_init = '请点击登录按钮'
MSG_error = '错误,请重新登录'
MSG_login = '小助手运行中'
MSG_scan = '请扫码二维码'
MSG_logout = '小助手成功退出'
MSG_reload = '重新启动'
MSG_remind = '小助手提醒中'

ITEM_LIST = [
    {'text':'登录', 'id':'login'},
    {'text':'聊天', 'id':'chat'},
    {'text':'日志', 'id':'log'},
    {'text':'设置', 'id':'setting'},
]

# Create your views here.

def index(request):
    'app初始界面, 有可能是唯一的界面'
    if HELPER.is_login:
        return run_page(request)
    else:
        return login_page(request)

def login(request, uuid=None):
    '终于登录了'
    try:
        if not uuid:
            inf, uuid = LG(QR_pic, 0)
            (msg, pic) = (MSG_scan, QR_pic) if inf == 'uuid' else (MSG_login, WX_pic)
            return JsonResponse(dict(
                status=True,
                inf=inf,
                uuid=uuid,
                msg=msg,
                pic=pic
            ))
        else:
            (status, msg) = (True, MSG_login) if LG(QR_pic, 1, uuid) else (False, MSG_error)
            return JsonResponse(dict(
                status=status,
                msg=msg,
                pic=WX_pic
            ))
    except EXCEPTIONS as error:
        info(error)
        HELPER.__init__()
        if os.path.isfile(QR_pic):
            os.remove(QR_pic)
        return JsonResponse(dict(
            status=False,
            msg=MSG_error,
            pic=WX_pic
        ))

def logout(request):
    '退出登录'
    HELPER.logout()
    return info_and_response(MSG_logout)

def remind(request):
    '提醒'
    HELPER.remind()
    HELPER.keep_alive()
    return info_and_response(MSG_remind)

def run_page(request):
    res = dict(
        status=HELPER.is_login,
        item_list=ITEM_LIST,
        page='login'
    )
    return render(request, 'helper/run.html', res)

def login_page(request):
    status = HELPER.is_login
    msg = MSG_login if status else MSG_init
    res = dict(
        status=status,
        msg=msg,
        pic=WX_pic
    )
    return render(request, 'helper/login.html', res)

def setting(request):
    return render(request, 'helper/setting.html')

def log(request):
    return render(request, 'helper/log.html')

def chat(request):
    return render(request, 'helper/chat.html')

def test_socket(request, client_id, channel):
    if not channel:
        return JsonResponse({'res':False, 'msg':'channel is empty'})
    if not client_id or client_id == 'null':
        client_id = str(uuid.uuid1())
    else:
        for count, client in enumerate(clients):
            if client[0] == client_id:
                if client[1] == channel:
                    #id 和 channel 都和已经连接的socket相同, 返回True
                    return JsonResponse({'res':True})
                else:
                    #id 相同, channel 不同, 删除该用户
                    del clients[count]
                    break

    #当指定socket未连接
    clients.append([client_id, channel, None])
    return JsonResponse({'res':False, 'client_id':client_id, 'msg':'no such connection'})

def close_socket(request, client_id):
    for count, client in enumerate(clients):
        if client[0] == client_id:
            del clients[count]
            return JsonResponse({'res':True})
    return JsonResponse({'res':False, 'msg':'no such id'})

@accept_websocket
def open_socket(request, client_id, channel):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            lock.acquire()
            #修改列表中对应的对象为socket
            for count, client in enumerate(clients):
                if client[0] == client_id and client[1] == channel:
                    num = count
                    client[2] = request.websocket
                    break

            #收到信息时的处理
            for message in request.websocket:
                if not message:
                    break
                print(message)
                #生成指定channel中的所有socket
                channel_socket_list = list(
                    map(lambda x: x[2],
                        list(filter(lambda x: True if x[1] == channel else False, clients)))
                )
                #发送消息
                for socket in channel_socket_list:
                    socket.send(message)
        finally:
            #当出错, 关掉这个socket
            clients[num][2].close()
            clients[num][2] = None
            lock.release()
    return HttpResponse('socket close')

def info_and_response(msg):
    '返回HTTP相应, 并输出日志'
    info(msg)
    return HttpResponse(msg)

def send_page(request):
    return render(request, 'helper/send.html')

def send_to_channel(request, content=None, channel=None):
    msg = send(content, channel)
    return HttpResponse(msg)

def get_log(request, start=0, count=1):
    log_list = log_read(count=int(count), start=int(start))
    return JsonResponse(dict(log_list=log_list))

def get_log_all(request):
    log_list = log_read(count=-1, start=0)
    return HttpResponse('<br>'.join(log_list))

def get_chat_user(request):
    user_list = []
    for user in HELPER.search_list():
        HELPER.get_head_img(user)
        user_list.append(user.nick_name)
    return JsonResponse(dict(user_list=user_list, count=len(user_list)))

@csrf_exempt
def chat_send(request):
    '主动发送消息'
    try:
        if request.method == 'POST':
            msg = request.POST['msg']
            user = request.POST['user']
            HELPER.send(msg, user)
            return JsonResponse(dict(res=True))
        else:
            raise NotImplementedError('访问错误')
    except EXCEPTIONS as error:
        return JsonResponse(dict(res=False, msg=error))


