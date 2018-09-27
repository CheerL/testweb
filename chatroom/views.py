import threading
import uuid
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Create your views here.


def base_view(request):
    return render(request, 'chatroom/index.html')


def send(request, text, channel):
    async_to_sync(get_channel_layer().group_send)(
        channel, {
            'type': 'chat_message',
            'message': {
                'channel': channel,
                'msg': text
            }
        })
    return HttpResponse('send %s to %s' % (text, channel))
