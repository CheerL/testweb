from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^art/(\d+)/(\d+)/(\d+)/(.*?)$', views.blog_read),
]
