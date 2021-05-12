# chat/consumers.py
'''
import json
from channels.generic.websocket import WebsocketConsumer



class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()

    def disconnect(self, close_code):
        pass

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message
        }))
'''

#types game_message, players_message

import random
import string

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Room, User

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


class ChatConsumer(WebsocketConsumer):


    def connect(self):

        with open("log.txt", 'a') as f:
            f.write(str(self.scope))
            f.write('\n')

        self.room_name = 'chat'#self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )



    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        payload = message['payload']
        name = message['sender']
        type = text_data_json['type']


        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
                {
                'type': 'chat_message',
                'message': message
                })


    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        sender = message['sender']
        payload = message['payload']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'sender': sender,
            'message': payload
        }))


class GameConsumer(WebsocketConsumer):


    def connect(self):

        with open("log.txt", 'a') as f:
            f.write(str(self.scope))
            f.write('\n')


        self.accept()


    def disconnect(self, close_code):
        # Leave room group
        r = Room.objects.get(room_name=self.room_name)
        r.n_connected -= 1
        if r.n_connected == 0:
            r.delete()
        else:
            r.save()


        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )



    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type = text_data_json['type']

        if type == 'look_up':
            num_players = message['num_players']
            player_name = message['player_name']

            self.player_name = player_name

            rooms = Room.objects.filter(n_demanded=num_players,
                                            n_connected__lte=num_players)
            if rooms.count() == 0:
                self.room_name = get_random_string(20)
                self.room_group_name = self.room_name

                r = Room(
                    n_demanded=num_players,
                    room_name = self.room_name,
                    n_connected=1
                    )

            else:

                r = rooms.first()
                self.room_name = r.room_name
                self.room_group_name = self.room_name
                r.n_connected += 1

            r.save()



            async_to_sync(self.channel_layer.group_add)(
                self.room_group_name,
                self.channel_name
            )

            u = User(user_name=player_name, room_id=r)
            u.save()



        # Send message to room group
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': "Player {} come in your room!".format(player_name)
                }
            )

    # Receive message from room group
    def game_message(self, event):
        message = event['message']

        client_adr, client_port = self.scope['client']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': '{}:{}$ {} '.format(client_adr, client_port, message) + str(Room.objects.get(room_name=self.room_name).n_connected)
        }))
