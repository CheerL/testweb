from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),

    url(r'^login/login/$', views.login),
    url(r'^login/init/$', views.login_init),
    url(r'^login/stop/$', views.login_stop),
    url(r'^login/logout/$', views.logout),

    url(r'^log/get/start=(?P<start>\d*)&count=(?P<count>-?\d*)$', views.get_log),
    url(r'^log/send/$', views.send_log),

    url(r'^chat/$', views.chat_page),
    url(r'^chat/user/', views.chat_user),
    url(r'^chat/send/', views.chat_send),

    url(r'^setting/init/$', views.get_setting),
    url(r'^setting/change/$', views.change_setting),

    # url(r'^send/$', views.send_page),
    # url(r'^send/login$', views.send_login),
    # url(r'^send/content=(?P<content>.*)&channel=(?P<channel>.*)$',
    #     views.send_to_channel),
]
