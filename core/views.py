from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_GET

from news.models import NewsArticle
from predictions.models import Match


def index(request):
    now = timezone.now()
    matches = Match.objects.filter(start_time__gt=now, status='scheduled').order_by('start_time')[:20]

    # Fetch 3 latest news items
    latest_news = NewsArticle.objects.order_by('-published_at')[:3]

    return render(request, 'core/index.html', {
        'matches': matches,
        'news': latest_news  # Pass to template
    })

# core/views.py updates
def about_view(request):
    return render(request, 'core/about.html')

def privacy_view(request):
    return render(request, 'core/privacy.html')

def tools_view(request):
    return render(request, 'core/calculator.html')


def match_detail(request, slug):
    match = get_object_or_404(Match, slug=slug)
    consensus = match.get_consensus_data()

    # Pass data for Chart.js
    chart_data = [0, 0, 0]
    if consensus:
        chart_data = [consensus['1'], consensus['X'], consensus['2']]

    return render(request, 'predictions/match_detail.html', {
        'match': match,
        'consensus': consensus,
        'chart_data': chart_data
    })

@require_GET
def ads_txt(request):
    """
    Serves the ads.txt file for Google AdSense.
    Replace 'pub-XXXXXXXXXXXXXXXX' with your ACTUAL AdSense Publisher ID.
    """
    # Standard Google format: google.com, pub-ID, DIRECT, ID
    # You find this line in your AdSense Dashboard -> Sites -> Add Site
    content = "google.com, pub-9012101234920620, DIRECT, f08c47fec0942fa0"
    return HttpResponse(content, content_type="text/plain")

@require_GET
def robots_txt(request):
    """
    Tells Google Bots what they can and cannot crawl.
    """
    lines = [
        "User-agent: *",
        "Disallow: /admin/",       # Don't look at admin
        "Disallow: /dashboard/",   # Don't look at dashboard
        "Allow: /",
        f"Sitemap: {request.scheme}://{request.get_host()}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")