from django.db import models
from markdownx.models import MarkdownxField
from markdownx.utils import markdownify
from urllib.parse import quote


def blog_image_path(instance, filename):
    title = quote(instance.title)
    filename = quote(filename)
    return 'images/blog_{0}/{1}'.format(title, filename)

# Create your models here.
class Blogs(models.Model):
    title = models.CharField(max_length=150)
    body = MarkdownxField()
    date = models.DateField()
    category = models.ForeignKey('Categorys', models.SET_NULL, null=True)
    cover = models.ImageField(
        upload_to=blog_image_path
    )

    def __str__(self):
        return self.title

    @property
    def markdown_body(self):
        return markdownify(self.body)

class Categorys(models.Model):
    name = models.CharField(max_length=10)

    def __str__(self):
        return self.name

