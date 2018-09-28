from django.conf.urls import url, include
from ssh import views

urlpatterns = [
    url(r'^$', views.login),
    url(r'^logout/', views.logout),
] 