#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waste_management.settings')
    
    # Setup Django
    django.setup()
    
    # Run migrations
    print("Running database migrations...")
    execute_from_command_line(['manage.py', 'migrate', '--noinput'])
    
    # Collect static files
    print("Collecting static files...")
    execute_from_command_line(['manage.py', 'collectstatic', '--noinput', '--clear'])
    
    # Start Gunicorn
    print("Starting Gunicorn server...")
    os.execvp('gunicorn', ['gunicorn', 'waste_management.wsgi'])
