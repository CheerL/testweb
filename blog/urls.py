from django.conf.urls import url
from blog import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^art/(\d+)/(\d+)/(\d+)/(.*?)$', views.blog_read),
]
