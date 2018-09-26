<<<<<<< HEAD
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.login),
    url(r'^logout/', views.logout),
=======
from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.login),
    url(r'^logout/', views.logout),
>>>>>>> 5143386867406b24d8fcdf3d540e4c7d00de1472
] 