from django.shortcuts import render
from .models import NewsArticle


def news_list(request):
    """
    Public page showing all latest football news.
    """
    # Get latest 50 articles
    articles = NewsArticle.objects.order_by('-published_at')[:50]

    return render(request, 'news/news_list.html', {
        'articles': articles,
        'page_title': 'Latest Football News - Kenya & World'
    })