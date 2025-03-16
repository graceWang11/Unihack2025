import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'interview_platform.settings')
django.setup()

# Run migrations
from django.core.management import call_command
print("Running migrations...")
call_command('migrate')
print("Migrations complete!")

# Create a superuser if needed
if len(sys.argv) > 1 and sys.argv[1] == '--create-superuser':
    from django.contrib.auth.models import User
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin')
        print("Superuser created!") 