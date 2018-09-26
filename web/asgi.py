import os
import django
from channels.routing import get_default_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")    #这里填的是你的配置文件settings.py的位置
django.setup()
application = get_default_application()
