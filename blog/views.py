from django.shortcuts import render
from .models import Blogs, Categorys

# Create your views here.
def get_category(result):
    result['category_list'] = [category.name for category in Categorys.objects.all()[:10]]

def index(request):
    blog_list = [
        {
            'pic':'/static/images/blog-1.jpg',
            'title':blog.title,
            'date':blog.date,
            'category':blog.category,
            'abstract':blog.body[:50],
            'href':'/'.join(['art', str(blog.date).replace('-', '/'), blog.title])
        } for blog in Blogs.objects.all()[:6]
    ]
    result = {
        'title':'Cheer.L Blog',
        'welcome':'欢迎来到Cheer.L的Blog',
        'pic':'/static/images/cover_bg_1.jpg',
        'blog_list':blog_list,
    }
    get_category(result)
    return render(request, 'blog/index.html', result)

def blog_read(request, year, month, day, title):
    date = '-'.join([str(year), str(month), str(day)])
    blog = Blogs.objects.get(date=date, title=title)
    result = {
        'title':blog.title,
        'body':blog.body,
        'writer':'Cheer.L',
        'date':blog.date,
        'pic':'/static/images/cover_bg_2.jpg'
    }
    get_category(result)
    return render(request, 'blog/view.html', result)
