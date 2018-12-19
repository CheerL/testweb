from django.contrib import admin
from markdownx.admin import MarkdownxModelAdmin
from blog.models import Blogs, Categorys

# Register your models here.
admin.site.register(Blogs, MarkdownxModelAdmin)
admin.site.register(Categorys)

