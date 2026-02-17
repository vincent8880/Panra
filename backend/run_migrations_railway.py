#!/usr/bin/env python
"""
Run migrations on Railway database.
Usage:
    export DATABASE_URL='postgresql://user:pass@host:port/dbname'
    python backend/run_migrations_railway.py
    
Or set DATABASE_URL directly:
    DATABASE_URL='postgresql://...' python backend/run_migrations_railway.py
"""
import os
import sys
import django

# Set DATABASE_URL if provided as argument
if len(sys.argv) > 1:
    os.environ['DATABASE_URL'] = sys.argv[1]

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

print("=" * 60)
print("RUNNING MIGRATIONS ON RAILWAY DATABASE")
print("=" * 60)

# Check DATABASE_URL
db_url = os.environ.get('DATABASE_URL', 'NOT SET')
if db_url == 'NOT SET':
    print("❌ ERROR: DATABASE_URL not set!")
    print("\nUsage:")
    print("  export DATABASE_URL='postgresql://user:pass@host:port/dbname'")
    print("  python backend/run_migrations_railway.py")
    print("\nOr:")
    print("  DATABASE_URL='postgresql://...' python backend/run_migrations_railway.py")
    sys.exit(1)

# Mask password in output
if '@' in db_url and ':' in db_url.split('@')[0]:
    masked_url = db_url.split('@')[0].split(':')[0] + ':***@' + '@'.join(db_url.split('@')[1:])
else:
    masked_url = db_url[:50] + '...' if len(db_url) > 50 else db_url

print(f"\nDatabase URL: {masked_url}")

# Run migrations
print("\nRunning migrations...")
try:
    execute_from_command_line(['manage.py', 'migrate'])
    print("\n✅ Migrations completed successfully!")
except Exception as e:
    print(f"\n❌ Error running migrations: {e}")
    sys.exit(1)












