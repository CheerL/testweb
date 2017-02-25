'默认初始页面视图'
from django.http import HttpResponse

def hello(request):
    'say: Hello world!'
    return HttpResponse("Hello world!")
