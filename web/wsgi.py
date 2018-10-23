"""
WSGI config for web project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from web.settings import STATICFILES_DIRS, STATIC_ROOT, DEBUG
#from whitenoise.django import DjangoWhiteNoise

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")

application = get_wsgi_application()
#application = WhiteNoise(application, root=STATIC_ROOT)

#if DEBUG:
#    for static_folder in STATICFILES_DIRS:
#        application.add_files(static_folder)
