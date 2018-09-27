from django.conf.urls import url
from chatroom import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = [
    url(r'^$', views.base_view)
]
