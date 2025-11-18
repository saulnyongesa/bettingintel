from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from predictions.models import Match
from news.models import NewsArticle
from django.utils import timezone


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return ['home', 'about', 'privacy', 'tools', 'news_list', 'all_predictions']

    def location(self, item):
        return reverse(item)


class MatchSitemap(Sitemap):
    changefreq = 'hourly'  # Matches change status/consensus often
    priority = 0.9

    def items(self):
        # Only index future matches or recently finished ones
        return Match.objects.filter(status='scheduled')

    def lastmod(self, obj):
        return obj.start_time


class NewsSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return NewsArticle.objects.all().order_by('-published_at')[:100]

    # News articles don't have a Detail View in your app (they link externally),
    # so we might technically skip this if you don't have internal pages for news.
    # But if you add a detail page later, this logic applies.
    # For now, since news links OUT, we usually don't map them in sitemap
    # unless we have a local page for them.
    # Let's keep matches as the priority.