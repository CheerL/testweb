from django.conf.urls import url
from helper.consumers import HelperConsumer

urlpatterns = [
    url(r'^(?P<channel>.*)/$', HelperConsumer),
]