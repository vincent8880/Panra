from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from markets.models import Market
from datetime import timedelta
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample prediction markets for testing'

    def handle(self, *args, **options):
        # Get or create a test user
        user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'credits': 10000.00,
                'base_credits': 10000.00,
                'max_credits': 10000.00
            }
        )
        
        if created:
            user.set_password('admin123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))

        # Sample markets
        markets_data = [
            {
                'title': 'Will Kenya win the 2024 AFCON?',
                'question': 'Will Kenya win the 2024 Africa Cup of Nations?',
                'description': 'Predict whether Kenya will win the 2024 AFCON tournament.',
                'category': 'Sports',
                'end_date': timezone.now() + timedelta(days=60),
            },
            {
                'title': 'Will it rain in Nairobi next week?',
                'question': 'Will there be measurable rainfall in Nairobi in the next 7 days?',
                'description': 'Predict if Nairobi will receive measurable rainfall (≥1mm) in the next week.',
                'category': 'Weather',
                'end_date': timezone.now() + timedelta(days=7),
            },
            {
                'title': 'Will the Kenyan Shilling strengthen against USD?',
                'question': 'Will KES/USD exchange rate be below 150 by end of Q1 2024?',
                'description': 'Predict if the Kenyan Shilling will strengthen to below 150 KES per USD by end of Q1 2024.',
                'category': 'Economics',
                'end_date': timezone.now() + timedelta(days=90),
            },
            {
                'title': 'Will Kenya host the 2025 World Athletics Championships?',
                'question': 'Will Kenya be selected as the host country for the 2025 World Athletics Championships?',
                'description': 'Predict if Kenya will be chosen to host the 2025 World Athletics Championships.',
                'category': 'Sports',
                'end_date': timezone.now() + timedelta(days=120),
            },
            {
                'title': 'Will M-Pesa introduce cryptocurrency trading?',
                'question': 'Will Safaricom M-Pesa launch cryptocurrency trading features in 2024?',
                'description': 'Predict if M-Pesa will add cryptocurrency trading capabilities in 2024.',
                'category': 'Technology',
                'end_date': timezone.now() + timedelta(days=365),
            },
        ]

        created_count = 0
        for market_data in markets_data:
            slug = market_data['title'].lower().replace(' ', '-').replace('?', '').replace(',', '')
            market, created = Market.objects.get_or_create(
                slug=slug,
                defaults={
                    **market_data,
                    'created_by': user,
                    'status': 'open',
                }
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created market: {market.title}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} sample markets!'))








