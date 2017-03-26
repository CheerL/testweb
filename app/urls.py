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
    url(r'^socket/test/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.test_socket),
    url(r'^socket/open/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.open_socket),
    url(r'^socket/close/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.close_socket),
    url(r'^send/$', views.send),
    url(r'^send/content=(?P<content>.*)&channel=(?P<channel>.*)$', views.send_to_channel),
]
