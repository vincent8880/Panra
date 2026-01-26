"""
User views for leaderboard and profile stats.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, F, Count, Sum
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from trading.models import Trade, Position
from markets.models import Market


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """User viewset for user management."""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            # Only show current user for list
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user."""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='credits')
    def credits(self, request):
        """Get current user's credits."""
        user = request.user
        return Response({
            'credits': float(user.credits),
            'current_credits': float(user.get_current_credits()),
            'credit_status': UserSerializer().get_credit_status(user)
        })


class LeaderboardViewSet(viewsets.ViewSet):
    """Leaderboard endpoints for rankings."""
    permission_classes = [AllowAny]  # Public leaderboard
    
    @action(detail=False, methods=['get'], url_path='all-time')
    def all_time(self, request):
        """Get all-time leaderboard (top 100)."""
        users = User.objects.filter(
            total_points__gt=0
        ).order_by('-total_points', '-accuracy_percentage')[:100]
        
        serializer = UserSerializer(users, many=True)
        return Response({
            'results': serializer.data,
            'type': 'all-time'
        })
    
    @action(detail=False, methods=['get'], url_path='weekly')
    def weekly(self, request):
        """Get weekly leaderboard (top 100)."""
        week_start = timezone.now() - timedelta(days=7)
        users = User.objects.filter(
            weekly_points__gt=0
        ).order_by('-weekly_points', '-accuracy_percentage')[:100]
        
        serializer = UserSerializer(users, many=True)
        return Response({
            'results': serializer.data,
            'type': 'weekly',
            'period_start': week_start
        })
    
    @action(detail=False, methods=['get'], url_path='monthly')
    def monthly(self, request):
        """Get monthly leaderboard (top 100)."""
        month_start = timezone.now() - timedelta(days=30)
        users = User.objects.filter(
            monthly_points__gt=0
        ).order_by('-monthly_points', '-accuracy_percentage')[:100]
        
        serializer = UserSerializer(users, many=True)
        return Response({
            'results': serializer.data,
            'type': 'monthly',
            'period_start': month_start
        })
    
    @action(detail=False, methods=['get'], url_path='around-me')
    def around_me(self, request):
        """Get user's rank plus 5 users above and below."""
        if not request.user.is_authenticated:
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        user_rank = User.objects.filter(
            total_points__gt=user.total_points
        ).count() + 1
        
        # Get users around this rank
        offset = max(0, user_rank - 6)
        users = User.objects.filter(
            total_points__gt=0
        ).order_by('-total_points', '-accuracy_percentage')[offset:offset+11]
        
        serializer = UserSerializer(users, many=True)
        return Response({
            'results': serializer.data,
            'user_rank': user_rank,
            'user_points': float(user.total_points)
        })


class UserStatsViewSet(viewsets.ViewSet):
    """User statistics and profile endpoints."""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's stats."""
        user = request.user
        stats = self._calculate_user_stats(user)
        return Response(stats)
    
    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get stats for a specific user (public)."""
        try:
            user = User.objects.get(pk=pk)
            stats = self._calculate_user_stats(user)
            return Response(stats)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def _calculate_user_stats(self, user):
        """Calculate comprehensive user statistics."""
        # Get positions
        positions = Position.objects.filter(user=user)
        active_positions = positions.exclude(
            yes_shares=0,
            no_shares=0
        ).count()
        
        # Get trades
        trades = Trade.objects.filter(
            Q(buyer=user) | Q(seller=user)
        )
        total_trades = trades.count()
        
        # Get markets traded
        markets_traded = Market.objects.filter(
            Q(trades__buyer=user) | Q(trades__seller=user)
        ).distinct().count()
        
        # Calculate unrealized P&L from positions
        unrealized_pnl = Decimal('0.00')
        for position in positions:
            if position.yes_shares > 0:
                current_value = position.yes_shares * position.market.yes_price
                cost_basis = position.yes_shares * position.yes_avg_cost
                unrealized_pnl += (current_value - cost_basis)
            if position.no_shares > 0:
                current_value = position.no_shares * position.market.no_price
                cost_basis = position.no_shares * position.no_avg_cost
                unrealized_pnl += (current_value - cost_basis)
        
        # Get rank
        rank = User.objects.filter(
            total_points__gt=user.total_points
        ).count() + 1
        
        # Get profile
        profile, _ = UserProfile.objects.get_or_create(user=user)
        
        return {
            'user': {
                'id': user.id,
                'username': user.username,
                'total_points': float(user.total_points),
                'weekly_points': float(user.weekly_points),
                'monthly_points': float(user.monthly_points),
                'rank': rank,
            },
            'trading': {
                'win_streak': user.win_streak,
                'best_win_streak': user.best_win_streak,
                'markets_predicted_correctly': user.markets_predicted_correctly,
                'total_markets_traded': user.total_markets_traded,
                'accuracy_percentage': float(user.accuracy_percentage),
                'roi_percentage': float(user.roi_percentage),
                'total_trades': total_trades,
                'markets_traded': markets_traded,
                'active_positions': active_positions,
            },
            'credits': {
                'current': float(user.get_current_credits()),
                'stored': float(user.credits),
                'max': float(user.max_credits),
            },
            'volume': {
                'total_volume_traded': float(profile.total_volume_traded),
                'total_profit_loss': float(profile.total_profit_loss),
                'unrealized_pnl': float(unrealized_pnl),
            }
        }
