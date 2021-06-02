from django.db import models

class Room(models.Model):
    room_name = models.CharField(max_length=50, primary_key=True)
    n_connected = models.IntegerField(default=0)
    n_demanded = models.IntegerField(default=0)
    n_ready = models.IntegerField(default=0)
    n_free = models.IntegerField(default=0)
    #time_creation = models.DateTimeField(blank=True)

class User(models.Model):
    class Meta:
        unique_together = (("user_name", "room_name"),)
    user_name = models.CharField(max_length=30, primary_key=True)
    #start_time = models.DateTimeField(blank=True)

    room_name = models.CharField(max_length=50)
    user_room_number = models.PositiveSmallIntegerField(default=0)
    status = models.CharField(max_length=10, default='waiting')
    num_cards = models.PositiveSmallIntegerField(default=0)
    score = models.IntegerField(default=0)
    is_free = models.BooleanField(default=False)
    #room_id = models.ForeignKey(Room, on_delete=models.CASCADE)
