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

# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from chat.models import Room

class ChatConsumer(WebsocketConsumer):
    def __init__(self, *args, **kwargs):

        
        super().__init__(*args, **kwargs)


    def connect(self):
        with open("log.txt", 'a') as f:
            f.write(str(self.scope))
            f.write('\n')

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name


        if Room.objects.all().count() == 0:
            Room(room_name=self.room_name, n_connected=1).save()

        else:
            r = Room.objects.get(room_name=self.room_name)
            r.n_connected += 1
            r.save()

    
        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept() 
        

    def disconnect(self, close_code):
        # Leave room group
        r = Room.objects.get(room_name=self.room_name)
        r.n_connected -= 1
        r.save()

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )


    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']

        client_adr, client_port = self.scope['client']

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': '{}:{}$ {} '.format(client_adr, client_port, message) + str(Room.objects.get(room_name=self.room_name).n_connected)
        }))
