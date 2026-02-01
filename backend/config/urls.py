"""
URL configuration for prediction market platform.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import CustomGoogleOAuth2CallbackView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/markets/', include('markets.urls')),
    path('api/trading/', include('trading.urls')),
    # Custom Google OAuth callback - must be before allauth.urls to override
    path('accounts/google/login/callback/', CustomGoogleOAuth2CallbackView.as_view(), name='google_callback'),
    path('accounts/', include('allauth.urls')),  # Allauth URLs for OAuth
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



