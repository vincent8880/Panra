from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet,
    LeaderboardViewSet,
    UserStatsViewSet,
    CsrfView,
    LoginView,
    LogoutView,
    SignupView,
    GoogleOAuthInitView,
    OAuthSuccessRedirectView,
)

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'stats', UserStatsViewSet, basename='stats')

urlpatterns = [
    path('csrf/', CsrfView.as_view(), name='auth-csrf'),
    path('login/', LoginView.as_view(), name='auth-login'),
    path('logout/', LogoutView.as_view(), name='auth-logout'),
    path('signup/', SignupView.as_view(), name='auth-signup'),
    path('google/init/', GoogleOAuthInitView.as_view(), name='auth-google-init'),
    path('oauth/success/', OAuthSuccessRedirectView.as_view(), name='oauth-success-redirect'),
] + router.urls


