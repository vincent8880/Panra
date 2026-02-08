"""
Management command to set up the Django Site domain.
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Set up the Django Site domain for Railway'

    def handle(self, *args, **options):
        # Determine the correct domain
        is_railway = os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('RAILWAY_PROJECT_ID')
        
        if is_railway:
            # Use Railway backend domain
            domain = os.getenv('RAILWAY_STATIC_URL', 'panra.up.railway.app')
            if not domain.startswith('http'):
                # Clean domain (remove protocol if present)
                domain = domain.replace('https://', '').replace('http://', '')
        else:
            domain = 'localhost:8001'
        
        try:
            # Get or create site with ID 1
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={'domain': domain, 'name': 'Panra'}
            )
            
            if not created:
                # Update existing site
                site.domain = domain
                site.name = 'Panra'
                site.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Updated Site domain to: {domain}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✅ Created Site with domain: {domain}'))
                
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Could not update Site: {e}'))








