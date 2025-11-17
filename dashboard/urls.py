from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_home, name='dashboard'),
    path('match/add/', views.add_match, name='add_match'),
    path('match/<int:match_id>/add-tip/', views.add_tip, name='add_tip'),
]