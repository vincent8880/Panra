"""
Management command to create or reset the admin superuser.
Usage: python manage.py setup_admin
       railway run python backend/manage.py setup_admin
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Create or reset the admin superuser (username: admin, password: admin123)'

    def handle(self, *args, **options):
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
                self.stdout.write(self.style.SUCCESS(f'✅ Updated admin user: {username}'))
            else:
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password
                )
                self.stdout.write(self.style.SUCCESS(f'✅ Created admin user: {username}'))

            self.stdout.write(f'\nAdmin credentials:')
            self.stdout.write(f'  Username: {username}')
            self.stdout.write(f'  Password: {password}')
            self.stdout.write(f'  → Log in at /admin/')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
