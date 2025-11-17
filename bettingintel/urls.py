
from django.contrib import admin
from django.urls import path, include
from core.views import index  # Import index directly for the homepage

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
]