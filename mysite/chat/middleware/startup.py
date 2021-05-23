from django.core.exceptions import MiddlewareNotUsed
from django.conf import settings
from chat.models import Room, User


class StartupMiddleware(object):
    def __init__(self, a):
        #print(a)
        # The following db settings name is django 1.2.  django < 1.2 will use settings.DATABASE_NAME
        Room.objects.all().delete()
        User.objects.all().delete()

        raise MiddlewareNotUsed('Startup complete')
