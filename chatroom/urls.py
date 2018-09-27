from django.conf.urls import url
from chatroom import views

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()


urlpatterns = [
    # Example:
    url(r'^$', views.base_view),
    url(r'^echo/client_id=(?P<client_id>.*)&channel=(?P<channel>.*)$', views.echo),
    url(r'^is-connection', views.is_connection),
    url(r'^close-connection', views.close_connection),
    url(r'^send/text=(?P<text>.*)&channel=(?P<channel>.*)', views.send),
    url(r'^test', views.test),
    # Uncomment the admin/doc line below and add 'django.contrib.admindocs'
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
]
