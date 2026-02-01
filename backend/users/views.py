"""
User views for authentication, leaderboard, and profile stats.
"""
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q, F, Count, Sum
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.middleware.csrf import get_token
from django.shortcuts import redirect, render
from django.conf import settings
from django.views import View
from allauth.socialaccount.providers.google.views import oauth2_login, OAuth2CallbackView
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.models import SocialAccount
from allauth.socialaccount.providers.google.provider import GoogleProvider
from datetime import timedelta
from decimal import Decimal
from .models import User, UserProfile
from .serializers import UserSerializer, UserProfileSerializer
from trading.models import Trade, Position
from markets.models import Market
import logging

logger = logging.getLogger(__name__)


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


class CsrfView(APIView):
    """
    Return CSRF token for the frontend to use with session-based auth.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        token = get_token(request)
        return Response({'csrfToken': token})


class LoginView(APIView):
    """
    Email/username + password login using Django sessions.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username') or request.data.get('email')
        password = request.data.get('password')

        if not username or not password:
            return Response(
                {'detail': 'Username/email and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try authentication with custom backend (supports email/username)
        user = authenticate(request, username=username, password=password)
        
        if user is None:
            # More specific error message
            return Response(
                {'detail': 'Invalid username/email or password. Please check your credentials and try again.'},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not user.is_active:
            return Response(
                {'detail': 'This account has been deactivated. Please contact support.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Log the user in (creates session)
        login(request, user)
        
        # Serialize user data
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """
    Log the current user out of their session.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SignupView(APIView):
    """
    Simple username/email/password signup.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')

        if not username or not email or not password:
            return Response(
                {'detail': 'Username, email, and password are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {'detail': 'Username already taken.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {'detail': 'Email already in use.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
        )

        # Optionally log them in immediately
        login(request, user)

        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GoogleOAuthInitView(APIView):
    """
    Return the Google OAuth URL for the frontend to redirect to.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        from django.urls import reverse
        
        # Use our custom Google OAuth flow (bypasses allauth's redirect mechanism)
        google_login_url = reverse('custom_google_login')
        full_url = request.build_absolute_uri(google_login_url)
        
        logger.info(f"GoogleOAuthInitView returning URL: {full_url}")
        
        return Response({
            'auth_url': full_url
        })


class OAuthSuccessRedirectView(APIView):
    """
    Redirect to frontend after successful OAuth.
    Uses a template with JavaScript redirect to avoid corrupted content errors.
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        from .utils import get_frontend_url
        
        # Get frontend URL
        frontend_url = get_frontend_url(request)
        redirect_url = f"{frontend_url}/?google_auth=success"
        
        logger.info(f"OAuthSuccessRedirectView rendering redirect page to: {redirect_url}")
        
        # Render a template that does a JavaScript redirect
        # This avoids HTTP redirect issues that cause corrupted content errors
        return render(request, 'socialaccount/login_redirect.html', {
            'redirect_url': redirect_url
        })


class CustomGoogleOAuth2CallbackView(View):
    """
    Custom Google OAuth callback - testing minimal response first.
    """
    
    def get(self, request, *args, **kwargs):
        from django.http import HttpResponse
        
        # STEP 1: First, let's just see if our view is being called at all
        # Return a simple HTML page without calling allauth
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>OAuth Callback Test</title>
</head>
<body style="background:#0a0a0a;color:#fff;font-family:sans-serif;padding:50px;">
    <h1>OAuth Callback Received!</h1>
    <p>This view is working. Now processing your login...</p>
    <p>If you see this page, the URL routing is working correctly.</p>
</body>
</html>'''
        
        response = HttpResponse(html, content_type='text/html')
        response['Cache-Control'] = 'no-store'
        return response


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
