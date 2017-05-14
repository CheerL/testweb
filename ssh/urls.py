from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^get_auth_obj/$', views.get_auth_obj),
]