#!/usr/bin/env python
"""
Update Django Site domain to Railway domain.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.sites.models import Site

# Get the current site (SITE_ID = 1)
site = Site.objects.get(id=1)

# Update to Railway domain
railway_domain = 'panra.up.railway.app'
site.domain = railway_domain
site.name = 'Panra'
site.save()

print(f"✅ Updated Site:")
print(f"   Domain: {site.domain}")
print(f"   Name: {site.name}")












