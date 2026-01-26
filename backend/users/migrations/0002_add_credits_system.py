# Generated migration for credits system
from django.db import migrations, models
from decimal import Decimal


def migrate_balance_to_credits(apps, schema_editor):
    """Migrate existing balance to credits, defaulting to 10000 if balance is 0."""
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        # If user has balance, use it; otherwise give them 10000 credits
        if user.balance and user.balance > 0:
            user.credits = user.balance
            user.base_credits = user.balance
            user.max_credits = max(user.balance, Decimal('10000.00'))
        else:
            user.credits = Decimal('10000.00')
            user.base_credits = Decimal('10000.00')
            user.max_credits = Decimal('10000.00')
        user.save()


def reverse_migration(apps, schema_editor):
    """Reverse migration: convert credits back to balance."""
    User = apps.get_model('users', 'User')
    for user in User.objects.all():
        user.balance = user.credits
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        # Add new credit fields
        migrations.AddField(
            model_name='user',
            name='credits',
            field=models.DecimalField(
                decimal_places=2,
                default=10000.00,
                help_text='Practice credits balance (starts at 10,000)',
                max_digits=20
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='last_activity_at',
            field=models.DateTimeField(
                auto_now=True,
                help_text='Last time user made a trade (used for decay calculation)',
                null=True
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='base_credits',
            field=models.DecimalField(
                decimal_places=2,
                default=10000.00,
                help_text='Base credits amount (used to calculate regeneration)',
                max_digits=20
            ),
        ),
        migrations.AddField(
            model_name='user',
            name='max_credits',
            field=models.DecimalField(
                decimal_places=2,
                default=10000.00,
                help_text='Maximum credits this user can have',
                max_digits=20
            ),
        ),
        # Migrate data
        migrations.RunPython(migrate_balance_to_credits, reverse_migration),
        # Remove old balance field
        migrations.RemoveField(
            model_name='user',
            name='balance',
        ),
    ]





















