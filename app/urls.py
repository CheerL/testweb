from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login$', views.login),
    url(r'^run$', views.run),
    url(r'^logout$', views.logout),
    url(r'^remind$', views.remind),
]
