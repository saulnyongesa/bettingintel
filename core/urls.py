from django.urls import path
from . import views

urlpatterns = [
    # We don't map the root '' here if it's mapped in the main config,
    # but we can map specific core pages.

    # Tools
    path('tools/kelly-criterion/', views.tools_view, name='tools'),

    # AdSense Mandatory Pages (Static)
    path('about-us/', views.about_view, name='about'),
    path('privacy-policy/', views.privacy_view, name='privacy'),
]