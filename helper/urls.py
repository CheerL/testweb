from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.index),
    url(r'^login/$', views.login_page),
    url(r'^run/$', views.run_page),

    url(r'^login_func/$', views.login),
    url(r'^logout/$', views.logout),

    url(r'^log/$', views.log_page),
    url(r'^log/all/', views.get_log_all),
    url(r'^log/get/start=(?P<start>\d*)&count=(?P<count>\d*)$', views.get_log),
    url(r'^log/send/$', views.send_log),

    url(r'^chat/$', views.chat_page),
    url(r'^chat/user/', views.get_chat_user),
    url(r'^chat/send/', views.chat_send),

    url(r'^setting/$', views.setting_page),
    url(r'^setting/change/$', views.setting_change),

    # url(r'^send/$', views.send_page),
    # url(r'^send/login$', views.send_login),
    # url(r'^send/content=(?P<content>.*)&channel=(?P<channel>.*)$',
    #     views.send_to_channel),
]
