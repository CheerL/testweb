from django.shortcuts import render
from blog.models import Blogs, Categorys
from urllib.parse import quote

TITLE_POSTFIX = 'Cheer.L Blog'

# Create your views here.
def get_category():
    return [category.name for category in Categorys.objects.all()[:10] if Blogs.objects.filter(category=category)]

def index(request):
    blog_list = [
        {
            'cover': quote(blog.cover.name),
            'title': blog.title,
            'date': blog.date,
            'category': blog.category.name,
            'abstract': blog.body[:50],
            'href': '/blog/' + '/'.join(['art', str(blog.date).replace('-', '/'), blog.title])
        } for blog in Blogs.objects.all()[:10]
    ]
    result = {
        'title': TITLE_POSTFIX,
        'welcome':'欢迎来到Cheer.L的Blog',
        'pic':'images/cover_bg_1.jpg',
        'blog_list':blog_list,
        'category_list': get_category(),
        'height': 800
    }
    return render(request, 'blog/index.html', result)

def blog_view(request, year, month, day, title):
    date = '-'.join([str(year), str(month), str(day)])
    blog = Blogs.objects.get(date=date, title=title)
    result = {
        'cover': quote(blog.cover.name),
        'title': blog.title,
        'body': blog.markdown_body,
        'writer': 'Cheer.L',
        'date': blog.date,
        'category_list': get_category()
    }
    return render(request, 'blog/view.html', result)

def category_view(request, category_name):
    category = Categorys.objects.get(name=category_name)
    blog_list = [
        {
            'cover': quote(blog.cover.name),
            'title': blog.title,
            'date': blog.date,
            'category': blog.category.name,
            'abstract': blog.body[:50],
            'href': '/blog/' + '/'.join(['art', str(blog.date).replace('-', '/'), blog.title])
        } for blog in Blogs.objects.filter(category=category)
    ]
    result = {
        'title':'{} -- {}'.format(category_name, TITLE_POSTFIX),
        'welcome': '{} 分类'.format(category_name),
        'pic':'images/cover_bg_1.jpg',
        'blog_list':blog_list,
        'category_list': get_category(),
        'height': 500
    }
    return render(request, 'blog/index.html', result)

