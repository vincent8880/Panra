from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, UserProfileSerializer
from .models import UserProfile

User = get_user_model()


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User viewset for viewing user data."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user's profile with credit status."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def credits(self, request):
        """Get current user's credit status with decay/regeneration info."""
        user = request.user
        serializer = self.get_serializer(user)
        return Response({
            'credits': serializer.data['current_credits'],
            'status': serializer.data['credit_status'],
        })



