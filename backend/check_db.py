#!/usr/bin/env python
"""
Check what database Railway backend is using.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.contrib.auth import get_user_model
from markets.models import Market

User = get_user_model()

print("=" * 60)
print("DATABASE CONNECTION INFO")
print("=" * 60)

# Check DATABASE_URL from environment
db_url = os.environ.get('DATABASE_URL', 'NOT SET')
print(f"\nDATABASE_URL from environment: {db_url[:50]}..." if len(db_url) > 50 else f"\nDATABASE_URL from environment: {db_url}")

# Check Django database config
db_config = connection.settings_dict
print(f"\nDjango Database Config:")
print(f"  Engine: {db_config.get('ENGINE', 'N/A')}")
print(f"  Name: {db_config.get('NAME', 'N/A')}")
print(f"  Host: {db_config.get('HOST', 'N/A')}")
print(f"  Port: {db_config.get('PORT', 'N/A')}")
print(f"  User: {db_config.get('USER', 'N/A')}")

# Check Railway environment variables
print(f"\nRailway Environment Variables:")
print(f"  RAILWAY_ENVIRONMENT: {os.environ.get('RAILWAY_ENVIRONMENT', 'NOT SET')}")
print(f"  RAILWAY_PROJECT_ID: {os.environ.get('RAILWAY_PROJECT_ID', 'NOT SET')}")

# Check data in database
print(f"\n" + "=" * 60)
print("DATA IN DATABASE")
print("=" * 60)
print(f"\nTotal Users: {User.objects.count()}")
print(f"Total Markets: {Market.objects.count()}")

if User.objects.exists():
    print(f"\nUsers:")
    for user in User.objects.all()[:5]:
        print(f"  - {user.username} (staff: {user.is_staff}, superuser: {user.is_superuser})")

if Market.objects.exists():
    print(f"\nMarkets:")
    for market in Market.objects.all()[:5]:
        print(f"  - {market.title}")

print("\n" + "=" * 60)


