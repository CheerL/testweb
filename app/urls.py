from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/(?P<uuid>.*)$', views.login),
    url(r'^logout$', views.logout),
    url(r'^remind$', views.remind),
    url(r'reload', views.reload),
]
