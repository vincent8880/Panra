#!/usr/bin/env python
import os
import django
from django.conf import settings
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

User = get_user_model()

# Admin credentials
username = 'admin'
email = 'ododovincent54@gmail.com'
password = 'admin123'

try:
    # Check if user exists
    user = User.objects.get(username=username)
    print(f"Admin user '{username}' already exists")
    
    # Update password and make sure they have correct permissions
    user.set_password(password)
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.email = email
    user.save()
    print(f"Updated admin user password and permissions")
    
except User.DoesNotExist:
    # Create new superuser
    user = User.objects.create_superuser(
        username=username,
        email=email,
        password=password
    )
    print(f"Created new admin user '{username}'")

print(f"✅ Admin login ready:")
print(f"   Username: {username}")
print(f"   Password: {password}")
print(f"   Email: {email}")
print(f"Total users: {User.objects.count()}")














