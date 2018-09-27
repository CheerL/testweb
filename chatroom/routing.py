from django.conf.urls import url
from chatroom.consumers import ChatConsumer

urlpatterns = [
    url(r'^client_id=(?P<client_id>[^/&]+)&channel=(?P<channel>[^/&]+)/$', ChatConsumer),
]