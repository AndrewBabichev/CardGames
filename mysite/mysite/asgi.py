"""
ASGI config for mysite project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""



import os
import sys
#BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#sys.path.append(BASE_DIR)
#os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'

#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
import django

django.setup()
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import chat.routing



application = ProtocolTypeRouter({
    "http": get_asgi_application(),

    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
