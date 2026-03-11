"""
Create 20 seed users with realistic Kenyan names and place bets to populate
the order book and leaderboard.

Run: python manage.py create_seed_users
"""
import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from markets.models import Market
from trading.models import Order
from users.models import UserProfile

User = get_user_model()

SEED_PASSWORD = 'Panra2026!'

SEED_USERS = [
    {'username': 'brian_ke', 'email': 'brian.ke@panra.test'},
    {'username': 'wanjiru254', 'email': 'wanjiru254@panra.test'},
    {'username': 'ochieng_d', 'email': 'ochieng.d@panra.test'},
    {'username': 'akinyi.mercy', 'email': 'akinyi.mercy@panra.test'},
    {'username': 'kiptoo_e', 'email': 'kiptoo.e@panra.test'},
    {'username': 'njeri_ann', 'email': 'njeri.ann@panra.test'},
    {'username': 'kamau.james', 'email': 'kamau.james@panra.test'},
    {'username': 'atieno_joy', 'email': 'atieno.joy@panra.test'},
    {'username': 'mwangi.pk', 'email': 'mwangi.pk@panra.test'},
    {'username': 'chebet_faith', 'email': 'chebet.faith@panra.test'},
    {'username': 'otieno.mark', 'email': 'otieno.mark@panra.test'},
    {'username': 'nyambura_g', 'email': 'nyambura.g@panra.test'},
    {'username': 'kipchoge_r', 'email': 'kipchoge.r@panra.test'},
    {'username': 'wambui.liz', 'email': 'wambui.liz@panra.test'},
    {'username': 'mutua_dan', 'email': 'mutua.dan@panra.test'},
    {'username': 'auma.stacy', 'email': 'auma.stacy@panra.test'},
    {'username': 'kibet.amos', 'email': 'kibet.amos@panra.test'},
    {'username': 'moraa_ciku', 'email': 'moraa.ciku@panra.test'},
    {'username': 'omondi.ray', 'email': 'omondi.ray@panra.test'},
    {'username': 'nyokabi_w', 'email': 'nyokabi.w@panra.test'},
]


class Command(BaseCommand):
    help = 'Create 20 seed users and place random bets on open markets'

    def add_arguments(self, parser):
        parser.add_argument(
            '--no-bets',
            action='store_true',
            help='Only create users, do not place bets.',
        )
        parser.add_argument(
            '--bets-per-user',
            type=int,
            default=3,
            help='Max bets per user (default 3). Actual count is random 1–N.',
        )

    def handle(self, *args, **options):
        place_bets = not options['no_bets']
        max_bets = options['bets_per_user']

        created_users = []
        for data in SEED_USERS:
            user, created = User.objects.get_or_create(
                username=data['username'],
                defaults={
                    'email': data['email'],
                    'credits': Decimal('10000.00'),
                    'base_credits': Decimal('10000.00'),
                    'max_credits': Decimal('10000.00'),
                },
            )
            if created:
                user.set_password(SEED_PASSWORD)
                user.save()
                UserProfile.objects.get_or_create(user=user)
                created_users.append(user)
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            else:
                self.stdout.write(f'Already exists: {user.username}')

        if not place_bets:
            self.stdout.write(self.style.SUCCESS(f'\nDone. Created {len(created_users)} users (no bets).'))
            return

        open_markets = list(Market.objects.filter(status='open'))
        if not open_markets:
            self.stdout.write(self.style.WARNING('No open markets found. Users created but no bets placed.'))
            return

        all_seed_users = list(
            User.objects.filter(username__in=[u['username'] for u in SEED_USERS])
        )

        total_orders = 0
        for user in all_seed_users:
            num_bets = random.randint(1, min(max_bets, len(open_markets)))
            markets_to_bet = random.sample(open_markets, num_bets)

            for market in markets_to_bet:
                side = random.choice(['yes', 'no'])
                price = market.yes_price if side == 'yes' else market.no_price
                quantity = Decimal(str(random.choice([10, 20, 50, 100, 150, 200])))
                cost = price * quantity

                if user.credits < cost:
                    continue

                order = Order.objects.create(
                    market=market,
                    user=user,
                    side=side,
                    order_type='market',
                    price=price,
                    quantity=quantity,
                    status='pending',
                )

                user.credits = max(Decimal('0.00'), user.credits - cost)
                user.base_credits = user.credits
                user.save(update_fields=['credits', 'base_credits'])

                market.total_volume += cost
                market.total_liquidity += cost
                market.save(update_fields=['total_volume', 'total_liquidity'])

                profile, _ = UserProfile.objects.get_or_create(user=user)
                profile.total_volume_traded = Decimal(str(profile.total_volume_traded)) + cost
                profile.save(update_fields=['total_volume_traded'])

                user.total_markets_traded = Order.objects.filter(
                    user=user
                ).values('market').distinct().count()
                user.total_points = user.calculate_points()
                user.save(update_fields=['total_markets_traded', 'total_points'])

                total_orders += 1
                self.stdout.write(
                    f'  {user.username} bet {quantity} on {side.upper()} @ {price} '
                    f'in "{market.title[:40]}..."'
                )

        # Try to match orders where possible
        self.stdout.write('\nMatching orders...')
        matched = 0
        try:
            from trading.matching import match_orders
            pending = Order.objects.filter(status='pending').order_by('created_at')
            for order in pending:
                try:
                    trades = match_orders(order)
                    if trades:
                        matched += len(trades)
                except Exception:
                    pass
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Matching skipped: {e}'))

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. Created {len(created_users)} users, '
                f'placed {total_orders} orders, matched {matched} trades.'
            )
        )
