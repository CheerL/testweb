import threading
import uuid
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
# from dwebsocket.decorators import accept_websocket
from django.views.decorators.csrf import csrf_exempt
# Create your views here.
def base_view(request):
    return render(request, 'chatroom/index.html')


clients = []

# @accept_websocket
def echo(request, client_id, channel):
    if request.is_websocket:
        lock = threading.RLock()
        try:
            index = None
            lock.acquire()
            for _index, _client in enumerate(clients):
                if _client[0] == client_id and _client[1] == channel:
                    index = _index
                    _client[2] = request.websocket
                    break
            for message in request.websocket:
                if not message:
                    break
                channel_socket_list = list(
                    map(lambda x: x[2],
                        list(filter(lambda x: True if x[1] == channel else False, clients)))
                )
                for socket in channel_socket_list:
                    socket.send(message)
        finally:
            clients[index][2].close()
            clients[index][2] = None
            lock.release()
    return HttpResponse()


@csrf_exempt
def is_connection(request):
    if request.method == 'POST':
        client_id = request.POST['client_id']
        channel = request.POST['channel']
        if not channel:
            return JsonResponse({'res': 'Error', 'msg': 'channel is empty'})
        if not client_id:
            client_id = str(uuid.uuid1())
        else:
            for _client_id, _channel, _ in clients:
                if _client_id == client_id:
                    if _channel == channel:
                        result = {
                            'res': 'True'
                        }
                        return JsonResponse(result)
                    else:
                        _channel = channel
                        break

        clients.append([client_id, channel, None])
        result = {
            'res': 'False',
            'client_id': client_id
        }
        return JsonResponse(result)
    return HttpResponse()


@csrf_exempt
def close_connection(request):
    if request.method == 'POST':
        client_id = request.POST['client_id']
        channel = request.POST['channel']
        if channel and client_id:
            for index, item in enumerate(clients):
                if item[0] == client_id:
                    clients.pop(index)
                    return JsonResponse({'res': 'successed'})
    return JsonResponse({'res': 'failed', 'msg': 'close connection failed'})


def send(request, text=None, channel=None):
    print(text, channel)
    for client in clients:
        if not channel or (channel and client[1] == channel):
            client[2].send(text.encode())
    return HttpResponse('send %s to %s' % (text, channel if channel else 'all'))


def test(request):
    return render(request, 'chatroom/test.html')