import random
import string
import asyncio

from datetime import datetime






# chat/consumers.py
import json
from asgiref.sync import async_to_sync, sync_to_async
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from chat.models import Room, User
from django.db.models import Sum

import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str


class Messages():

    @staticmethod
    def set_players(attack_player, response_player):
        msg = {
            'type': 'game_message',
            'message': {
                'action_type':'players',
                'sender': 'GAME_SERVER',
                'info':{
                    'attack_player':attack_player,
                    'response_player':response_player
                },
                'time': datetime.now().strftime("%H:%M:%S")

            }
        }

        return msg

class ChatConsumer(AsyncWebsocketConsumer):


    async def connect(self):

        #with open("log.txt", 'a') as f:
        #    f.write(str(self.scope))
        #    f.write('\n')

        #print("Scope:", self.scope)
        self.room_name = 'chat'#self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = self.room_name

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        #print("accepted")


    async def disconnect(self, close_code):
        # Leave room group

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )



    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json['message']
        payload = message['payload']
        name = message['sender']
        type = text_data_json['type']


        await self.channel_layer.group_send(
            self.room_group_name,
                {
                'type': 'chat_message',
                'message':{
                    'sender': name,
                    'payload': payload,
                    'time': datetime.now().strftime("%H:%M:%S")
                }
                })


    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message
            }))


class DatabaseHandler():

    @staticmethod
    @database_sync_to_async
    def get_count(db, kv_dict):
        return db.objects.filter(**kv_dict).count()


    @staticmethod
    @database_sync_to_async
    def get_rooms_number(num_players):

        n_rooms = Room.objects.filter(n_demanded=num_players,
                                        n_connected__lte=num_players).count()
        return n_rooms


    @staticmethod
    @database_sync_to_async
    def get_num_players(room_name):

        r = Room.objects.get(room_name=room_name)

        return r.n_connected

    @staticmethod
    @database_sync_to_async
    def createRoom(num_players):
        room_name = get_random_string(30)

        r = Room(
            n_demanded=num_players,
            room_name = room_name,
            n_connected=1
            )
        r.save()

        return  r

    @staticmethod
    @database_sync_to_async
    def addUser2room(n_demanded):
        rooms = Room.objects.filter(n_demanded=n_demanded,
                                        n_connected__lte=n_demanded)
        r = rooms.first()
        room_name = r.room_name
        r.n_connected += 1

        r.save()

        return r

    @staticmethod
    @database_sync_to_async
    def pop_from_room(room_name):
        r = Room.objects.get(room_name=room_name)
        r.n_connected -= 1
        #self.connected -= 1
        if r.n_connected == 0:
            r.delete()
        else:
            r.save()

    @staticmethod
    @database_sync_to_async
    def add_user(user_name, room_name):
        num_connected = User.objects.filter(room_name=room_name).all().count()
        u = User( user_name=user_name,
                  room_name=room_name,
                  user_room_number=num_connected,
                  status='wait_game',
                  num_cards=0
                )

        u.save()

        return u


    @staticmethod
    @database_sync_to_async
    def delete_user(user_name, room_name):
        u = User.objects.filter(user_name=user_name, room_name=room_name)
        u.delete()

    @staticmethod
    @database_sync_to_async
    def create_random(room_name):
        num_connected = Room.objects.get(room_name=room_name).n_connected
        print(num_connected)
        r = random.randint(0, num_connected-1)
        attack_player = User.objects.filter(room_name=room_name)[r].user_name
        response_player = User.objects.filter(
                            room_name=room_name
                            )[(r + 1) % num_connected].user_name
        print("Players:", attack_player, response_player)

        return (attack_player, response_player)

    @staticmethod
    @database_sync_to_async
    def get_user_names(room_name):
        user_names = User.objects.filter(room_name=room_name).values_list(
                                                        'user_name', flat=True)

        return list(user_names)


    @staticmethod
    @database_sync_to_async
    def get_users(room_name):
        users = User.objects.filter(room_name=room_name).all()

        return users

    @staticmethod
    @database_sync_to_async
    def set_user_values(user_name, room_name, key_value):
        user = User.objects.get(user_name=user_name, room_name=room_name)
        user.update(**key_value)

        user.save()

        return user

    @staticmethod
    @database_sync_to_async
    def get_user_cards(user_name, room_name, num_cards=1):
        user = User.objects.get(user_name=user_name, room_name=room_name)
        user.num_cards += num_cards
        user.save()

        return user.num_cards

    @staticmethod
    @database_sync_to_async
    def give_user_cards(user_name, room_name):
        user = User.objects.get(user_name=user_name, room_name=room_name)
        user.num_cards -= 1
        user.save()

        return user.num_cards


    @staticmethod
    @database_sync_to_async
    def set_random(room_name):
        users = User.objects.filter(room_name=room_name).all()
        users.update(status='addition')
        num_users = users.count()


        attack_user_num = random.randint(0, num_users-1)
        response_user_num = (attack_user_num + 1) % num_users

        attack_user = users[attack_user_num]
        attack_user_name = users[attack_user_num].user_name

        attack_user.status='attack'
        attack_user.save()


        response_user = users[response_user_num]
        response_user_name = response_user.user_name

        response_user.status='response'
        response_user.save()

        print("Users:", attack_user_name, response_user_name)

        return (attack_user_name, response_user_name)

    @staticmethod
    @database_sync_to_async
    def set_after_round(room_name, responser_take=True):


        users = User.objects.filter(room_name=room_name)
        count = Room.objects.get(room_name=room_name).n_demanded
        responser_pos = users.get(status='response').user_room_number
        attacker_pos = users.get(status='attack').user_room_number
        users.update(status='addition')

        i = 1
        while users.get(user_room_number= (responser_pos + i) % count ).is_free:
            i += 1

        first_free = (responser_pos + i)  % count

        j = 1
        while users.get(user_room_number= (first_free + j) % count).is_free:
            j += 1

        second_free = (first_free + j) % count

        if responser_take:

            attacker_pos = first_free
            responser_pos = second_free
        else:
            if users.get(user_room_number=responser_pos).num_cards:
                attacker_pos = responser_pos
                responser_pos = first_free
            else:
                attacker_pos = first_free
                responser_pos = second_free

        attacker = users.get(user_room_number=attacker_pos)
        attacker.status = 'attack'
        attacker.save()
        attacker_name = attacker.user_name

        responser = users.get(user_room_number=responser_pos)
        responser.status = 'response'
        responser.save()
        responser_name = responser.user_name

        return attacker_name, responser_name


    @staticmethod
    @database_sync_to_async
    def create_right_users_order(room_name):
        attack_user = User.objects.get(room_name=room_name, status='attack').user_name
        response_user = User.objects.get(room_name=room_name, status='response').user_name

        addition_users = User.objects.filter(room_name=room_name,
                                            status='addition').values_list('user_name', flat=True)

        return [attack_user, *list(addition_users), response_user]



    @staticmethod
    @database_sync_to_async
    def check_that_all_taken(room_name):
        users = User.objects.filter(room_name=room_name).all()
        for u in users:
            if u.num_cards < 6:
                return True
        return False

    @staticmethod
    @database_sync_to_async
    def get_num_cards(user_name, room_name):
        user = User.objects.get(user_name=user_name, room_name=room_name)
        return user.num_cards

    @staticmethod
    @database_sync_to_async
    def get_total_num_cards(room_name):
        return User.objects.filter(room_name=room_name)\
                .aggregate(Sum('num_cards'))['num_cards__sum']

    @staticmethod
    @database_sync_to_async
    def increase_n_ready(room_name):
        r = Room.objects.get(room_name=room_name)
        r.n_ready += 1
        r.save()
        return r.n_ready


    @staticmethod
    @database_sync_to_async
    def reset_n_ready(room_name):
        r = Room.objects.get(room_name=room_name)
        r.n_ready = 0
        r.save()

        return r.n_ready

    @staticmethod
    @database_sync_to_async
    def find_user_with_cards(room_name):
        user = User.objects.get(room_name=room_name, num_cards__gt=0)

        return user.user_name

    @staticmethod
    @database_sync_to_async
    def get_free(room_name):
        n_free = Room.objects.get(room_name=room_name).n_free

        return n_free

    @staticmethod
    @database_sync_to_async
    def increase_free(room_name, value=1):
        r = Room.objects.get(room_name=room_name)
        r.n_free += value
        r.save()

        return r.n_free


    @staticmethod
    @database_sync_to_async
    def reset_room(room_name, value=0):
        r = Room.objects.get(room_name=room_name)
        r.n_free = value
        r.n_ready = value
        r.save()

        return r


    @staticmethod
    @database_sync_to_async
    def reset_connected(room_name, value=0):
        r = Room.objects.get(room_name=room_name)
        r.connected = value
        r.save()

        return r


    @staticmethod
    @database_sync_to_async
    def increase(room_name, attrname, increase_on):
        assert hasattr(Room, attrname)

        r = Room.objects.get(room_name=room_name)
        room_attr = getattr(r, attrname)
        room_attr += increase_on
        r.save()

        return r

    @staticmethod
    @database_sync_to_async
    def reset_users(room_name):
        users = User.objects.filter(room_name=room_name)
        users.update(num_cards=0, status='waiting', is_free=False)


        return users.count()

    @staticmethod
    @database_sync_to_async
    def increase_score(user_name, room_name, increase_on=0):
        user = User.objects.get(room_name=room_name, user_name=user_name)
        user.score += increase_on
        user.save()

        return user.score

    @staticmethod
    @database_sync_to_async
    def get_user_score(user_name, room_name):
        user = User.objects.get(room_name=room_name, user_name=user_name)
        return user.score

    @staticmethod
    @database_sync_to_async
    def set_user_free(user_name, room_name):
        user = User.objects.get(user_name=user_name, room_name=room_name)
        user.is_free = True
        user.save()

        return user.is_free

class CardGetter():
    def __init__(self):
        self.reset()

    def shuffle(self):

        random.shuffle(self.cards)

    def get(self):
        if len(self.cards):
            return self.cards.pop()
        else:
            return None, None

    def return_card(self, card_type, card_value):
        self.cards.insert(0, (card_type, card_value))

    def size(self):
        return len(self.cards)

    def reset(self):
        self.cards = [(i, j) for i in range(0, 4)
                            for j in range(4, 13)]

#CARD_GETTER = CardGetter()
GLOBAL_VARIABLES_DICT = {}
#print("upper card_getter", CARD_GETTER)

class GameConsumer(AsyncWebsocketConsumer):


    async def users_take(self):

        user_names = await DatabaseHandler.get_user_names(self.room_name)

        users_have =  await DatabaseHandler.get_total_num_cards(self.room_name)
        deck_size = self.card_getter.size()
        print(users_have, deck_size)
        num_cards = users_have + deck_size


        if GLOBAL_VARIABLES_DICT[self.room_name]['state'] != 'START':
            user_names = await DatabaseHandler.create_right_users_order(
                                                                self.room_name)
        else:
            user_names = await DatabaseHandler.get_user_names(self.room_name)


        print(num_cards)
        n_users = await DatabaseHandler.get_num_players(self.room_name)
        indicator = 1 if num_cards % n_users else 0
        each_should_have = min(num_cards // n_users +  indicator, 6, self.card_getter.size())
        print(each_should_have)
        for user_name in user_names:
            user_num_cards = await DatabaseHandler.get_num_cards(user_name,
                                                                self.room_name)
            #print("User name:", user_name, user_num_cards)

            user_should_take = max(each_should_have - user_num_cards, 0)
            if user_should_take == 0:
                continue



            await self.channel_layer.group_send(
                #'{}_{}'.format(user_name, self.room_group_name),
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': {
                        'action_type':'take_cards',
                        'sender': "GAME_SEVER",
                        'action_info':{
                            'user_name': user_name,
                            'num_cards' : user_should_take
                        },
                        'time': datetime.now().strftime("%H:%M:%S")

                    }
                }
            )

            return False

        return True





    async def set_roles(self):
        state = GLOBAL_VARIABLES_DICT[self.room_name]['state']
        if state == 'START':
            attacker_name, responser_name = \
                        await DatabaseHandler.set_random(self.room_name)


        elif state == 'TAKE':
            print("STATE:", "TAKE")
            attacker_name, responser_name = \
                    await DatabaseHandler.set_after_round(
                                            self.room_name,
                                            True)
        elif state == 'READY':
            print("STATE", "READY")
            attacker_name, responser_name = \
                    await DatabaseHandler.set_after_round(
                                            self.room_name,
                                            False)


        if state != "IDLE":
            await self.channel_layer.group_send(
                self.room_group_name,
                Messages.set_players(attacker_name, responser_name)
                )

        GLOBAL_VARIABLES_DICT[self.room_name]['state'] = "IDLE"


    async def update_scores(self):
        users_scores = await self.get_users_scores()
        #print(users_scores)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': {
                    'action_type':'users_scores',
                    'sender': 'GAME_SERVER',
                    'action_info':{
                        'scores':users_scores
                    },
                    'time': datetime.now().strftime("%H:%M:%S")

                }})

    async def start_game(self):
        GLOBAL_VARIABLES_DICT[self.room_name]['state'] = 'START'
        #GLOBAL_VARIABLES_DICT[self.room_name]['num_free'] = 0
        self.card_getter.reset()
        self.card_getter.shuffle()
        card_type, card_value = self.card_getter.get()
        self.card_getter.return_card(card_type, card_value)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': {
                    'action_type':'royal_card',
                    'sender': 'GAME_SERVER',
                    'action_info':{
                        'card_type': card_type,
                        'card_value': card_value,
                    },
                    'time': datetime.now().strftime("%H:%M:%S")

                }
            })




        await DatabaseHandler.reset_room(self.room_name)
        await DatabaseHandler.reset_users(self.room_name)

        await self.users_take()

    async def ask_repeat(self):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'game_message',
                'message': {
                    'action_type':'repeat',
                    'sender': 'GAME_SERVER',
                    'time': datetime.now().strftime("%H:%M:%S")

                }
            })


    async def increase_scores(self, looser_player=None):
        user_names = await DatabaseHandler.get_user_names(self.room_name)
        for user_name in user_names:
            if looser_player is None:
                await DatabaseHandler.increase_score(user_name,
                                                    self.room_name,
                                                    1)
            else:
                if user_name != looser_player:
                    await DatabaseHandler.increase_score(user_name,
                                                        self.room_name,
                                                        2)

    async def get_users_scores(self):
        user_names = await DatabaseHandler.get_user_names(self.room_name)
        users_scores = {}
        for user_name in user_names:
            user_score = await DatabaseHandler.get_user_score(user_name, self.room_name)
            users_scores[user_name] = user_score

        return users_scores


    async def connect(self):


        await self.accept()


    async def disconnect(self, close_code=0):
        # Leave room group


        await self.channel_layer.group_send(
            self.room_group_name,
                {
                'type': 'game_message',
                'message':{
                    'action_type': 'disconnect_message',
                    'sender': self.user_name,
                    'time': datetime.now().strftime("%H:%M:%S")
                }
                })

        await DatabaseHandler.delete_user(self.user_name, self.room_name)

        await DatabaseHandler.pop_from_room(self.room_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )





    # Receive message from WebSocket
    async def receive(self, text_data):
        print("recieve data:", text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        type = text_data_json['type']

        if type == 'look_up':

            #print("Lower getter:", self.card_getter)
            self.num_players = message['num_players']
            self.user_name = message['player_name']

            if  await DatabaseHandler.get_rooms_number(self.num_players):
                room = await DatabaseHandler.addUser2room(self.num_players)
            else:
                room = await DatabaseHandler.createRoom(self.num_players)
                GLOBAL_VARIABLES_DICT[room.room_name] = {}
                GLOBAL_VARIABLES_DICT[room.room_name]['card_getter'] = CardGetter()
                GLOBAL_VARIABLES_DICT[room.room_name]['state'] = 'IDLE'
                GLOBAL_VARIABLES_DICT[room.room_name]['repeat_game'] = 0


            self.state = GLOBAL_VARIABLES_DICT[room.room_name]['state']
            self.card_getter = GLOBAL_VARIABLES_DICT[room.room_name]['card_getter']


            self.room_name, self.connected = room.room_name, room.n_connected


            await DatabaseHandler.add_user(self.user_name, self.room_name)


            self.room_group_name = self.room_name
            self.user_group_name = "{}_{}".format(self.user_name,
                                                self.room_group_name)

            await self.channel_layer.group_add(
                self.user_group_name,
                self.channel_name
            )

            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )


            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'game_message',
                    'message': {
                        'action_type':'player_addition',
                        'sender': self.user_name,
                        'time': datetime.now().strftime("%H:%M:%S")

                    }}
            )


            if self.connected == self.num_players:
                await self.update_scores()
                await self.start_game()



        elif type == 'game_message':

            if message['action_type'] == 'get_card':
                await DatabaseHandler.get_user_cards(self.user_name, self.room_name)
                card_type, card_value = self.card_getter.get()
                if card_type is None:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_message',
                            'message': {
                                'action_type':'empty_deck',
                                'sender': 'GAME_SERVER',
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })
                else:
                    await self.channel_layer.group_send(
                        self.user_group_name,
                        {
                            'type': 'game_message',
                            'message': {
                                'action_type':'get_card',
                                'sender': 'GAME_SERVER',
                                'action_info':{
                                    'to': self.user_name,
                                    'card_type': card_type,
                                    'card_value': card_value,
                                    'deck_size': self.card_getter.size()
                                },
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })


                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_message',
                            'message': {
                                'action_type':'another_user_get',
                                'sender': 'GAME_SERVER',
                                'action_info':{
                                    'deck_size': self.card_getter.size()
                                },
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })


            elif message['action_type'] == 'all_cards_taken':
                print("Getter size:", self.card_getter.size())
                if self.card_getter.size() == 0:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_message',
                            'message': {
                                'action_type':'empty_deck',
                                'sender': 'GAME_SERVER',
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })
                    await self.set_roles()
                else:
                    all_take = await self.users_take()
                    if all_take:
                        await self.set_roles()


            elif message['action_type'] == 'player_free':

                await DatabaseHandler.set_user_free(message['sender'], self.room_name)

                n_free = await DatabaseHandler.increase_free(self.room_name)
                n_players = await DatabaseHandler.get_num_players(self.room_name)
                if n_free == n_players:
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'game_message',
                            'message': {
                                'action_type':'drawn',
                                'sender': 'GAME_SERVER',
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })

                    await self.increase_scores()
                    await self.update_scores()

                    await DatabaseHandler.reset_connected(self.room_name)
                    await asyncio.sleep(1)

                    await self.ask_repeat()


            elif message['action_type'] ==  'player_ready':


                # do it throught database
                GLOBAL_VARIABLES_DICT[self.room_name]['state'] = 'READY'

                n_ready = await DatabaseHandler.increase_n_ready(self.room_name)


                n_free = await DatabaseHandler.get_free(self.room_name)
                n_players = await DatabaseHandler.get_num_players(self.room_name)
                print('DEBUG n_ready: {} {}'.format(n_ready, n_players))
                if n_free == n_players-1:
                    user_with_cards = await DatabaseHandler.find_user_with_cards(self.room_name)

                    await self.channel_layer.group_send(
                        self.room_group_name,
                            {
                            'type': 'game_message',
                            'message':{
                                'action_type': 'user_loose',
                                'sender': user_with_cards,
                                'time': datetime.now().strftime("%H:%M:%S")
                            }
                        })


                    await self.increase_scores(user_with_cards)
                    await self.update_scores()
                    await DatabaseHandler.reset_connected(self.room_name)
                    await asyncio.sleep(1)
                    await self.ask_repeat()
                    return

                if n_ready == n_players - n_free -1:

                    await self.channel_layer.group_send(
                        self.room_group_name,
                    {
                            'type': 'game_message',
                            'message': {
                                'action_type':'ready',
                                'sender': 'GAME_SERVER',
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })




                    all_have = await self.users_take()



                    if all_have:
                        await self.set_roles()


                    await DatabaseHandler.reset_n_ready(self.room_name)


            elif message['action_type'] == 'player_take':

                GLOBAL_VARIABLES_DICT[self.room_name]['state'] = 'TAKE'
                num_cards = message['action_info']['num_cards']

                n_free = await DatabaseHandler.get_free(self.room_name)
                n_players = await DatabaseHandler.get_num_players(self.room_name)

                if n_free == n_players -1:

                    await self.channel_layer.group_send(
                        self.room_group_name,
                            {
                            'type': 'game_message',
                            'message':{
                                'action_type': 'user_loose',
                                'sender': self.user_name,
                                'time': datetime.now().strftime("%H:%M:%S")
                            }
                        })


                    await self.increase_scores(self.user_name)
                    await self.update_scores()

                    await DatabaseHandler.reset_connected(self.room_name)
                    await asyncio.sleep(1)

                    await self.ask_repeat()
                    return


                await DatabaseHandler.get_user_cards(self.user_name,
                                                        self.room_name,
                                                        num_cards)
                await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                        'type': 'game_message',
                        'message':{
                            **message,
                            'time': datetime.now().strftime("%H:%M:%S")
                        }
                    })

                await DatabaseHandler.reset_n_ready(self.room_name)

                all_have = await self.users_take()

                if all_have:
                    await self.set_roles()


            elif message['action_type'] == 'repeat_game':

                if message['action_info']['answer'] == 'yes':

                    await DatabaseHandler.increase(self.room_name, 'n_connected', 1)

                    #GLOBAL_VARIABLES_DICT[self.room_name]['repeat_game'] += 1
                    n_players = await DatabaseHandler.get_num_players(self.room_name)
                    print("n_connected {} n_demanded : {}".format(n_players, self.num_players))
                    if n_players == self.num_players:
                        await self.start_game()

                elif message['action_info']['answer'] == 'no':
                    print("no answer")
                    await self.channel_layer.group_send(
                        self.room_group_name,
                            {
                            'type': 'game_message',
                            'message':{
                                'action_type': 'info',
                                'sender': 'GAME_SEVER',
                                'action_info':{
                                    'info': 'Player {} leave your room'\
                                    .format(message['sender'])
                                },

                                'time': datetime.now().strftime("%H:%M:%S")
                            }
                        })


                    #await self.disconnect()

            else:


                if message['action_type'] == 'card_response' or \
                                message['action_type'] == 'card_addition':

                    await DatabaseHandler.give_user_cards(message['sender'],
                                                            self.room_name)


                GLOBAL_VARIABLES_DICT['state'] = "Attack"
                await self.channel_layer.group_send(
                    self.room_group_name,
                        {
                        'type': 'game_message',
                        'message':{
                            **message,
                            'time': datetime.now().strftime("%H:%M:%S")
                        }
                    })


                await DatabaseHandler.reset_n_ready(self.room_name)
                if  message['action_type'] == 'card_response' and \
                                not message['action_info']['remain_cards']:

                    await self.channel_layer.group_send(
                        self.room_group_name,
                    {
                            'type': 'game_message',
                            'message': {
                                'action_type':'ready',
                                'sender': 'GAME_SERVER',
                                'time': datetime.now().strftime("%H:%M:%S")

                            }
                        })



    # Receive message from room group
    async def game_message(self, event):
        #message = event['message']
        print("Send:", event)
        message = event['message']
        if message['action_type'] == 'players':
            users = await DatabaseHandler.get_user_names(self.room_name)
            self.attack_id = users.index(message['info']['attack_player'])
            self.response_id = users.index(message['info']['response_player'])
        # Send message to WebSocket
        await self.send(text_data=json.dumps(event))
