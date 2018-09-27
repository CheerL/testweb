from django.conf.urls import url
from chatroom.consumers import ChatConsumer

urlpatterns = [
    url(r'^chatroom/channel=(?P<channel>[^/&]+)/$', ChatConsumer),
]