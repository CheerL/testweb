from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/uuid=(?P<uuid>.*)$', views.login),
    url(r'^login/$', views.login_page),
    url(r'^run/$', views.run_page),
    url(r'^logout/$', views.logout),
    url(r'^remind$', views.remind),
    url(r'^setting/$', views.setting),
    url(r'^log/$', views.log),
    url(r'^chat/$', views.chat),
]
