from datetime import timedelta

from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from django.utils import timezone

from .models import Match, League, Tip


def prediction_list(request):
    # 1. Base Query: Future matches only
    now = timezone.now()
    matches = Match.objects.filter(status='scheduled', start_time__gt=now).select_related('league').order_by('start_time')

    # 2. Filtering Logic
    league_slug = request.GET.get('league')
    date_filter = request.GET.get('date') # 'today', 'tomorrow'

    if league_slug:
        matches = matches.filter(league__slug=league_slug)

    if date_filter == 'today':
        end_of_day = now.replace(hour=23, minute=59)
        matches = matches.filter(start_time__range=(now, end_of_day))
    elif date_filter == 'tomorrow':
        start_tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0)
        end_tomorrow = (now + timedelta(days=1)).replace(hour=23, minute=59)
        matches = matches.filter(start_time__range=(start_tomorrow, end_tomorrow))

    # 3. Pagination (20 matches per page)
    paginator = Paginator(matches, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # 4. Context Data
    leagues = League.objects.annotate(match_count=Count('match')).filter(match_count__gt=0).order_by('-match_count')

    context = {
        'matches': page_obj,
        'leagues': leagues,
        'current_league': league_slug,
        'current_date': date_filter
    }
    return render(request, 'predictions/match_list.html', context)


def league_detail(request, league_slug):
    """
    SEO Page: Shows predictions specific to one league (e.g., /predictions/premier-league/)
    """
    league = get_object_or_404(League, slug=league_slug)
    matches = Match.objects.filter(league=league, status='scheduled') \
        .order_by('start_time')

    context = {
        'league': league,
        'matches': matches,
        'page_title': f'{league.name} Betting Tips & Predictions'
    }
    return render(request, 'predictions/league_detail.html', context)


def match_detail(request, slug):
    """
    THE MONEY PAGE.
    Displays the analysis, consensus, and charts for a specific match.
    """
    match = get_object_or_404(Match, slug=slug)

    # 1. Fetch all tips for this match with source info to avoid N+1 queries
    all_tips = match.tips.select_related('source').all()

    # 2. Separate "Trusted" sources (Accuracy > 55%) from others
    # This adds "Programmatic Value" by filtering bad advice
    trusted_tips = [t for t in all_tips if t.source.accuracy_score >= 55.0]
    other_tips = [t for t in all_tips if t.source.accuracy_score < 55.0]

    # 3. Get Consensus Data (Using the method we added to the Model)
    consensus = match.get_consensus_data()

    # 4. Prepare Data for Chart.js (Must be a simple list: [Home%, Draw%, Away%])
    # We handle the case where consensus is None (no tips yet)
    if consensus:
        chart_data = [consensus['1'], consensus['X'], consensus['2']]
    else:
        chart_data = [0, 0, 0]  # Empty chart

    context = {
        'match': match,
        'trusted_tips': trusted_tips,
        'other_tips': other_tips,
        'consensus': consensus,
        'chart_data': chart_data,
        'total_votes': len(all_tips)
    }

    return render(request, 'predictions/match_detail.html', context)


from django.shortcuts import render

# Create your views here.
