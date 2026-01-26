from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, LeaderboardViewSet, UserStatsViewSet

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'leaderboard', LeaderboardViewSet, basename='leaderboard')
router.register(r'stats', UserStatsViewSet, basename='stats')

urlpatterns = router.urls



