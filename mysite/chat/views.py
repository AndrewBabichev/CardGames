from django.shortcuts import render
from django.http import JsonResponse

from chat.models import Room, User

from datetime import datetime

def index(request):


    return render(request, 'chat/index.html')

def room(request, room_name):
    return render(request, 'chat/room.html', {
        'room_name': room_name
    })
