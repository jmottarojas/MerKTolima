#!/usr/bin/env python3
"""Script to run the Django frontend server."""

import os
import sys
import django
from django.core.management import execute_from_command_line
from django.conf import settings

def main():
    """Run Django development server."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'merkatolima_frontend.settings')
    
    # Change to frontend directory
    frontend_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(frontend_dir)
    
    print("🌐 Starting Merktolima Frontend Server...")
    print(f"📍 Frontend will be available at: http://localhost:8001")
    print(f"🔗 Make sure the API server is running at: http://localhost:8000")
    print("=" * 60)
    
    # Run Django server
    sys.argv = ['manage.py', 'runserver', '0.0.0.0:8001']
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()