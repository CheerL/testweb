import threading
import uuid
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt


# Create your views here.
def base_view(request):
    return render(request, 'chatroom/index.html')
