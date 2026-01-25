#!/usr/bin/env python
"""
Script to create a Django superuser non-interactively.
Usage: python create_admin.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create superuser
username = os.environ.get('ADMIN_USERNAME', 'admin')
email = os.environ.get('ADMIN_EMAIL', 'admin@panra.com')
password = os.environ.get('ADMIN_PASSWORD', 'admin123')

if User.objects.filter(username=username).exists():
    # Update existing user
    user = User.objects.get(username=username)
    user.set_password(password)
    user.email = email
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save()
    print(f'✅ Updated existing user {username}')
else:
    # Create new superuser
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f'✅ Created new superuser {username}')

print(f'\nAdmin credentials:')
print(f'Username: {username}')
print(f'Email: {email}')
print(f'Password: {password}')
print(f'\nTotal users in database: {User.objects.count()}')




