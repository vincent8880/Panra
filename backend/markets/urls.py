from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import MarketViewSet

router = DefaultRouter()
router.register(r'', MarketViewSet, basename='market')

urlpatterns = router.urls



