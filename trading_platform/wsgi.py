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

# NOTE: Creating admin users at import time is unsafe for production and can
# cause side effects during management commands. If you need an automated
# admin creation step, run `python create_admin.py` or implement a
# dedicated management command that is executed explicitly.
