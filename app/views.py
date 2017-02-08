from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    result = {
        'body':'This is an App.'
    }
    return render(request, 'app/index.html', result)
