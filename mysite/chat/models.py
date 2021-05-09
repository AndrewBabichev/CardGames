from django.db import models

class Room(models.Model):
    room_name = models.CharField(max_length=30)
    n_connected = models.IntegerField()
    
