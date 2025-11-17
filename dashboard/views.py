from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from news.models import NewsArticle
from predictions.models import Match, League, Source, Tip
from django.contrib import messages
from django.http import HttpResponse

@login_required
def dashboard_home(request):
    stats = {
        'total_matches': Match.objects.count(),
        'active_matches': Match.objects.filter(status='scheduled').count(),
        'total_tips': Tip.objects.count()
    }

    # Fetch recent matches
    recent_matches = Match.objects.order_by('-start_time')[:5]

    # Fetch recent news (New Addition)
    latest_news = NewsArticle.objects.order_by('-published_at')[:6]

    context = {
        'stats': stats,
        'matches': recent_matches,
        'news': latest_news  # <--- Pass to template
    }
    return render(request, 'dashboard/home.html', context)

def add_match(request):
    # You will link a ModelForm here later
    return HttpResponse("Add Match Form goes here")

def add_tip(request, match_id):
    # You will link a ModelForm here later
    return HttpResponse(f"Add Tip for Match ID {match_id}")