"""
WSGI config for trading_platform project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'trading_platform.settings')

application = get_wsgi_application()
# Force admin creation on server startup
from django.contrib.auth.models import User
try:
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'Pass12345')
        print("Admin user created successfully on startup!")
except Exception as e:
    print(f"Error creating admin: {e}")

