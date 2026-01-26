#!/usr/bin/env python
"""
Script to update admin user email.
Usage: python update_admin_email.py
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Get new email from environment
new_email = os.environ.get('ADMIN_EMAIL')
if not new_email:
    print('Error: ADMIN_EMAIL environment variable not set')
    print('Usage: export ADMIN_EMAIL=your-email@example.com && python update_admin_email.py')
    exit(1)

try:
    admin_user = User.objects.get(username='admin')
    admin_user.email = new_email
    admin_user.save()
    print(f'Admin email updated to: {new_email}')
except User.DoesNotExist:
    print('Admin user not found!')

