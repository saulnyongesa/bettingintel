from django.urls import path
from . import views

urlpatterns = [
    path('', views.prediction_list, name='all_predictions'),
    path('league/<slug:league_slug>/', views.league_detail, name='league_detail'),
    path('<slug:slug>/', views.match_detail, name='match_detail'),
]
