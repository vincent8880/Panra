"""
Management command to set up Google OAuth SocialApp in database.
Run this after setting GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from decouple import config
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Set up Google OAuth SocialApp in database'

    def handle(self, *args, **options):
        client_id = config('GOOGLE_OAUTH_CLIENT_ID', default='')
        secret = config('GOOGLE_OAUTH_CLIENT_SECRET', default='')
        
        if not client_id or not secret:
            self.stdout.write(
                self.style.WARNING(
                    '⚠️  GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET not set. Skipping Google OAuth setup.'
                )
            )
            return
        
        # Get or create the site
        site = Site.objects.get_current()
        
        # Get or create the SocialApp
        social_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google',
                'client_id': client_id,
                'secret': secret,
            }
        )
        
        if not created:
            # Update existing
            social_app.client_id = client_id
            social_app.secret = secret
            social_app.save()
            self.stdout.write(self.style.SUCCESS('✅ Updated Google OAuth SocialApp'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ Created Google OAuth SocialApp'))
        
        # Add site to social app
        if site not in social_app.sites.all():
            social_app.sites.add(site)
            self.stdout.write(self.style.SUCCESS(f'✅ Added site {site.domain} to SocialApp'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Google OAuth configured:'))
        self.stdout.write(f'   Client ID: {client_id[:20]}...')
        self.stdout.write(f'   Site: {site.domain}')

