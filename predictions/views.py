from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Match, League, Tip


def prediction_list(request):
    """
    Lists all upcoming matches ordered by date.
    Good for the 'All Predictions' page.
    """
    matches = Match.objects.filter(status='scheduled') \
        .select_related('league') \
        .order_by('start_time')

    context = {
        'matches': matches,
        'page_title': 'All Football Betting Tips & Predictions'
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
