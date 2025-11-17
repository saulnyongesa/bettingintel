from django.shortcuts import render, get_object_or_404
from django.utils import timezone

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

