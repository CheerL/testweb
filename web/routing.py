from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.conf.urls import url, include
from chatroom.routing import urlpatterns as chatroom_urlpatterns
from helper.routing import urlpatterns as helper_urlpatterns

application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': AuthMiddlewareStack(
        URLRouter(
            chatroom_urlpatterns + helper_urlpatterns
        )
    ),
})
