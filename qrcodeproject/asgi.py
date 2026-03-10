"""
ASGI config for qrcodeproject project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.1/howto/deployment/asgi/
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'qrcodeproject.settings')

# Setup Django first
django.setup()

from django.core.asgi import get_asgi_application

# Try to import Channels components
try:
    from channels.routing import ProtocolTypeRouter, URLRouter
    from channels.auth import AuthMiddlewareStack
    from django.urls import path
    
    # Lazy import consumers to avoid circular imports
    def get_websocket_patterns():
        from conductorapp.consumers import BusTrackingConsumer, AdminDashboardConsumer
        return [
            path('ws/tracking/bus/<int:bus_id>/', BusTrackingConsumer.as_asgi()),
            path('ws/admin/dashboard/', AdminDashboardConsumer.as_asgi()),
        ]
    
    django_asgi_app = get_asgi_application()
    
    application = ProtocolTypeRouter({
        'http': django_asgi_app,
        'websocket': AuthMiddlewareStack(
            URLRouter(
                get_websocket_patterns()
            )
        ),
    })
except Exception as e:
    # Fallback to regular Django ASGI if Channels is not properly configured
    import logging
    logging.warning(f"Channels not available: {e}. Using standard Django ASGI.")
    application = get_asgi_application()

