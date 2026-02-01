"""
URL configuration for prediction market platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.google_oauth import GoogleOAuthStartView, GoogleOAuthCallbackView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/markets/', include('markets.urls')),
    path('api/trading/', include('trading.urls')),
    
    # Custom Google OAuth - bypasses allauth's redirect mechanism
    path('auth/google/', GoogleOAuthStartView.as_view(), name='custom_google_login'),
    path('auth/google/callback/', GoogleOAuthCallbackView.as_view(), name='custom_google_callback'),
    
    # Keep allauth for other functionality
    path('accounts/', include('allauth.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



