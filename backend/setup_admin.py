#!/usr/bin/env python
"""
Check database connection and create/update admin user.
Run this on Railway: railway run python backend/setup_admin.py
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
print("DATABASE CONNECTION CHECK")
print("=" * 60)

# Check database connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        print("✅ Database connection: SUCCESS")
except Exception as e:
    print(f"❌ Database connection: FAILED - {e}")
    exit(1)

# Check database info
db_config = connection.settings_dict
print(f"\nDatabase Info:")
print(f"  Engine: {db_config.get('ENGINE', 'N/A')}")
print(f"  Database: {db_config.get('NAME', 'N/A')}")
print(f"  Host: {db_config.get('HOST', 'N/A')}")

# Check existing data
print(f"\n" + "=" * 60)
print("EXISTING DATA")
print("=" * 60)
print(f"Total Users: {User.objects.count()}")
print(f"Total Markets: {Market.objects.count()}")

# Create/Update Admin User
print(f"\n" + "=" * 60)
print("CREATING/UPDATING ADMIN USER")
print("=" * 60)

username = 'admin'
email = 'ododovincent54@gmail.com'
password = 'admin123'

try:
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.is_active = True
        user.save()
        print(f"✅ Updated existing admin user: {username}")
    else:
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"✅ Created new admin user: {username}")
    
    print(f"\nAdmin Credentials:")
    print(f"  Username: {username}")
    print(f"  Email: {email}")
    print(f"  Password: {password}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    
except Exception as e:
    print(f"❌ Error creating admin: {e}")
    exit(1)

# Verify
print(f"\n" + "=" * 60)
print("VERIFICATION")
print("=" * 60)
print(f"Total Users: {User.objects.count()}")
print(f"Total Markets: {Market.objects.count()}")

if Market.objects.exists():
    print(f"\nSample Markets:")
    for market in Market.objects.all()[:3]:
        print(f"  - {market.title}")

print(f"\n✅ Setup complete! You can now log in at /admin/")
print("=" * 60)

