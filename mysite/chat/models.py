from django.db import models

class Room(models.Model):
    room_id =  models.AutoField(primary_key=True, default=0)
    room_name = models.CharField(max_length=20)
    n_connected = models.IntegerField(default=0)
    n_demanded = models.IntegerField(default=0)
    #time_creation = models.DateTimeField(blank=True)

class User(models.Model):
    user_id =  models.AutoField(primary_key=True)
    user_name = models.CharField(max_length=30)
    #start_time = models.DateTimeField(blank=True)
    room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
