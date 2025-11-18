
from django.contrib import admin
from django.urls import path, include
from core.views import index  # Import index directly for the homepage
from django.contrib.sitemaps.views import sitemap
from core.views import index, ads_txt, robots_txt # Import new views
from core.sitemaps import StaticViewSitemap, MatchSitemap

# Define Sitemaps Dictionary
sitemaps = {
    'static': StaticViewSitemap,
    'matches': MatchSitemap,
}
urlpatterns = [
    path('admin/', admin.site.urls),

    # 1. Homepage (Root)
    path('', index, name='home'),

    # 2. Core Pages (Tools, About, Privacy)
    path('info/', include('core.urls')),

    # 3. Predictions (Matches, Leagues)
    path('predictions/', include('predictions.urls')),

    # 4. Dashboard (Protected Area)
    path('dashboard/', include('dashboard.urls')),
    path('news/', include('news.urls')),
    path('ads.txt', ads_txt, name='ads_txt'),
    path('robots.txt', robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]