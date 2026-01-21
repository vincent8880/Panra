from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import OrderViewSet, TradeViewSet, PositionViewSet

router = DefaultRouter()
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'trades', TradeViewSet, basename='trade')
router.register(r'positions', PositionViewSet, basename='position')

urlpatterns = router.urls



