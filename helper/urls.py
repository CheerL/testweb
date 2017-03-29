from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_page),
    url(r'^run/$', views.run_page),

    url(r'^login/uuid=(?P<uuid>.*)$', views.login),
    url(r'^logout/$', views.logout),

    url(r'^log/$', views.log_page),
    url(r'^log/all/', views.get_log_all),
    url(r'^log/get/start=(?P<start>\d*)&count=(?P<count>\d*)$', views.get_log),

    url(r'^socket/test/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.test_socket),
    url(r'^socket/open/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.open_socket),
    url(r'^socket/close/client_id=(?P<client_id>.*)$', views.close_socket),
    url(r'^send/$', views.send_page),
    url(r'^send/content=(?P<content>.*)&channel=(?P<channel>.*)$', views.send_to_channel),

    url(r'^chat/$', views.chat_page),
    url(r'^chat/user/', views.get_chat_user),
    url(r'^chat/send/', views.chat_send),

    url(r'^setting/$', views.setting_page),
    url(r'^setting/change/$', views.setting_change),
]
