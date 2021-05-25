"""Classes for fool-online game."""

import tkinter as tk
import numpy as np
import tkinter.font as font

from PIL import Image, ImageTk
from os.path import join
from playsound import playsound
from functools import partial


import json

PLAYERS_TYPES = ['atack', 'responce', 'addition']
STATUS = 'Attacked'


class Card(tk.Button):
    """Special Button Class containins image for card and card type."""

    def __init__(self, parent=None, card_id=None, image=None, **kwargs):

        self.image = image
        self.card_id = card_id
        super().__init__(parent, image=self.image, **kwargs)

# Card that have position in the hand


class PlayerCard(Card):
    """Card that have index in player hand"""

    def __init__(
            self,
            parent=None,
            card_id=None,
            image=None,
            index=None,
            **kwargs):
        self.index = index
        super().__init__(parent, card_id, image, **kwargs)
# -------------------------------------------------------------------------------


class CardsCreator():
    """Class for creating card objects contains paths to image resourses."""

    def __init__(self, image_dir=None):
        """image_dir - directory with images"""
        self.image_dir = image_dir
        self.cards_images = np.zeros((4, 13), dtype=tk.PhotoImage)
        self.PIL_images = {}

        for i in range(0, self.cards_images.shape[0]):
            for j in range(0, self.cards_images.shape[1]):
                name = join(
                    self.image_dir, '{}_{}.png'.format(
                        str(i), str(
                            j + 1)))
                self.PIL_images[i, j] = Image.open(name)
                self.cards_images[i, j] = ImageTk.PhotoImage(
                    self.PIL_images[i, j])

        self.empty_image = tk.PhotoImage(
            file=join(self.image_dir, 'empty.png'))
        self.back_image = tk.PhotoImage(file=join(self.image_dir, 'back.png'))

    def create_card(self, parent, cards_id, relief='groove', transform=None):
        """return created card"""
        if transform == 'rotate':
            image = ImageTk.PhotoImage(
                self.PIL_images[cards_id[0], cards_id[1]].transpose(
                    Image.ROTATE_90)
            )
        else:
            image = self.cards_images[cards_id[0], cards_id[1]]

        c = Card(parent,
                 card_id=cards_id,
                 image=image,
                 relief=relief)

        return c


class SimpleDeck(CardsCreator, tk.Frame):
    """Deck class that give player card."""

    def __init__(self, parent=None, image_dir=None, row=0, referee=None):
        CardsCreator.__init__(self, image_dir)
        tk.Frame.__init__(self, parent)

        self.row = row
        self.referee = referee
        self.size = 36

        self.deck_cards = []
        self.deck_pos_x = 0.02
        self.deck_pos_y = 0.3
        self.update()

    def update(self):
        for deck_card in self.deck_cards:
            deck_card.destroy()

        self.deck_cards = []

        indicator = 1 if self.size > 1 else 0
        for i in range(int(self.size / 5) + indicator):
            self.deck_cards.append(
                tk.Button(
                    self.master,
                    image=self.back_image,
                    state=tk.DISABLED))
            self.deck_cards[-1].place(relx=self.deck_pos_x - i * 0.002,
                                      rely=self.deck_pos_y - i * 0.002)
            self.deck_cards[-1].bind('<Button-1>', self.referee.get_card)

    def destroy(self):
        for deck_card in self.deck_cards:
            deck_card.destroy()

    def reset(self):
        self.size = 36
        self.update()


class FoolDeck(SimpleDeck):
    """SimpleDeck that have royal card"""

    def __init__(
            self,
            parent,
            image_dir,
            row=0,
            referee=None,
            royal_card=None):

        self.royal_card = royal_card
        self.royal_card_btn = tk.Button(None)
        super().__init__(parent, image_dir, row, referee)

    def update(self):

        self.royal_card_btn.destroy()

        if self.royal_card and self.size:
            self.royal_card_btn = self.create_card(
                self.master, self.royal_card, transform='rotate')
            self.royal_card_btn.bind('<Button-1>', self.referee.get_card)
            self.royal_card_btn.place(
                relx=self.deck_pos_x + 0.025,
                rely=self.deck_pos_y + 0.03)

        SimpleDeck.update(self)

    def destroy(self):
        SimpleDeck.destroy(self)

        self.royal_card_btn.destroy()


class Table(tk.Button):
    """Container for current cards"""

    def __init__(self, parent, relwidth, relheight, columns=2, referee=None):
        """
        relwidth, relheight - size in relative coords
        colunms - have many cards suited in row
        referee - special object for controlling game consistency
        """

        super().__init__(parent, bg='green', state=tk.DISABLED)
        self.place(relx=0.18, rely=0.1, relheight=relheight, relwidth=relwidth)

        self.columns = columns
        self.referee = referee

        self.empty_row = 0
        self.empty_column = 0
        self.cards_values = set()
        self.a_cards = {}
        self.r_cards = {}

    def add_card(self, card_type, card_value):
        """
        draw attack card on table.
        """
        card = self.referee.deck.create_card(self, (card_type, card_value))
        card.grid(
            row=self.empty_row,
            column=self.empty_column,
            padx=40,
            pady=40)

        self.cards_values.add(card_value)
        self.a_cards[(card_type, card_value)] = card
        self.empty_row += 1 if self.empty_column == self.columns - 1 else 0
        self.empty_column = (self.empty_column + 1) % self.columns

    def response(self, r_card, a_card):
        """
        draw response card upon attacker card.
        r_card - Card object from responser
        a_card - Card object from attacker
        """

        x, y = a_card.winfo_x(), a_card.winfo_y()

        c = self.referee.deck.create_card(self, r_card.card_id)
        c.place(x=x + 25, y=y + 25)

        a_card = self.a_cards[a_card.card_id]

        a_card['state'] = tk.DISABLED
        self.r_cards[r_card.card_id] = c
        self.r_cards[a_card.card_id] = a_card
        self.a_cards.pop(a_card.card_id)

        self.cards_values.add(r_card.card_id[1])

    def reset(self):

        self.empty_row = 0
        self.empty_column = 0
        self.card_values = set()

        for card in list(self.a_cards.values()) + list(self.r_cards.values()):
            card.destroy()

        self.a_cards.clear()
        self.r_cards.clear()


class Referee(object):
    """
    Special class for game controlling game consistency
    have acess to player, deck, table and score_table
    can change their states
    """


    def __init__(
            self,
            player=None,
            deck=None,
            table=None,
            info=None,
            score_table=None):

        self.player = player
        self.deck = deck
        self.table = table
        self.info = info
        self.score_table = score_table

    def add_card_on_table(self, card):
        """
        Check that player can add card on table
        Add card on table if this card is allowed.
        """
        def addition():
            self.table.add_card(card.card_id[0], card.card_id[1])
            self.player.cards.pop(card.index)
            card.destroy()

            self.table['state'] = tk.DISABLED
            self.player.update()

        card_type, card_value = card.card_id

        if self.player.status == 'attack':
            addition()
            self.player.status = 'addition'
            print(self.player.ready)
            self.player.ready['state'] = tk.ACTIVE
            return card_type, card_value

        elif self.player.status == 'addition':
            if card.card_id[1] in self.table.cards_values:
                addition()
                return card_type, card_value
            else:
                self.info.set("Not allowed operation")
                return None

    def response(self, r_card, a_card):
        """
        If player must response
        controlling that player can add response card on table.
        """
        def can_response(r_card, a_card):
            less = a_card.card_id[0] == r_card.card_id[0] and\
                a_card.card_id[1] < r_card.card_id[1]

            royal = r_card.card_id[0] == self.royal_card[0] and \
                a_card.card_id[0] != self.royal_card[0]

            print("response:", less, royal)

            return royal or less

        is_response = can_response(r_card, a_card)
        if is_response:
            self.player.deleteCard(r_card)
            if not len(self.table.a_cards):
                self.player.take['state'] = tk.DISABLED
        return is_response

    def take(self):
        """
        if player cannot reposponse on cards,
        referee give table cards to him
        """
        if self.player.status == 'response':
            addition_cards = list(self.table.a_cards.values()) +\
                list(self.table.r_cards.values())

            self.player.cards += addition_cards
            self.player.update()
            self.table.reset()

            return len(addition_cards)

    def set_atack_player(self):
        self.player.status = 'attack'
        self.info.set("You attack!")

    def set_response_player(self):
        self.player.status = 'response'
        self.info.set("You response!")

    def set_addition_player(self):
        self.player.status = 'addition'
        self.player.ready['state'] = tk.ACTIVE
        self.info.set("You add!")

    def make_cards_active(self):
        for card in self.table.a_cards.values():
            card['state'] = tk.ACTIVE
            card.bind('<Button-1>',
                      partial(self.player.action, card))


class OnlineReferee(Referee):
    """
    Referee that have online connection and
    send player actions on server and recieve messages from it
    """

    def __init__(self, game_socket, chat_socket, player=None,
                 deck=None, table=None, info=None, score_table=None):
        """
        game_socket - socket for game messages
        chat_socket - socket for char message
        """
        self.game_socket = game_socket
        self.chat_socket = chat_socket

        super().__init__(player, deck, table, info, score_table)

    def add_card_on_table(self, card):
        """add card on table and send message about it."""
        card = Referee.add_card_on_table(self, card)

        if card is not None:
            msg = json.dumps({
                'type': 'game_message',
                'message': {
                    'sender': self.player.name,
                    'action_type': 'card_addition',
                    'description': "Player {} add card ({}, {})".format(
                        self.player.name,
                        card[0], card[1]
                    ),
                    'action_info': {
                        'card_type': card[0],
                        'card_value': card[1],
                        'remain_cards': len(self.player.cards)
                    }
                }
            })

            self.game_socket.send(msg)

            if not len(self.player.cards):
                self.ready()

            if not len(self.player.cards) and not self.deck.size:

                self.__free_user()

    def response(self, r_card, a_card):
        """add reponse card and send message about it."""
        is_response = Referee.response(self, r_card, a_card)

        if is_response:
            msg = json.dumps({
                'type': 'game_message',
                'message': {
                    'sender': self.player.name,
                    'action_type': 'card_response',
                    'description': "Player {} response card \
                                        ({}, {}) on ({}, {})".format(
                        self.player.name, r_card.card_id[0], r_card.card_id[1],
                        a_card.card_id[0], a_card.card_id[1]),
                    'action_info': {
                        'a_card_type': a_card.card_id[0],
                        'a_card_value': a_card.card_id[1],

                        'r_card_type': r_card.card_id[0],
                        'r_card_value': r_card.card_id[1],

                        'remain_cards': len(self.player.cards)
                    }
                }
            })

            self.game_socket.send(msg)

        if not len(self.player.cards) and not self.deck.size:
            self.__free_user()

    def take(self):
        num_cards = Referee.take(self)

        msg = json.dumps({
            'type': 'game_message',
            'message': {
                'action_type': 'player_take',
                'sender': self.player.name,
                'description': "Player {}\
                                    take cards!".format(self.player.name),
                'action_info': {
                    'player_name': self.player.name,
                    'num_cards': num_cards
                }
            }
        })

        self.player.state = 'wait'
        self.game_socket.send(msg)

    def ready(self):
        msg = json.dumps({
            'type': 'game_message',
            'message': {
                'action_type': 'player_ready',
                'sender': self.player.name,
                'desctiption': "Player {} cannot add card!",
                'action_info': {
                    'player_name': self.player.name
                }
            }
        })
        self.player.ready['state'] = tk.DISABLED
        self.player.state = 'wait'
        self.game_socket.send(msg)

    def __send_all_taken(self):
        msg = json.dumps({
            'type': 'game_message',
            'message': {
                'action_type': 'all_cards_taken',
                'sender': self.player.name,
            }})
        self.game_socket.send(msg)
        self.info.set("Wait other players!")
        self.player.state = 'all_cards_taken'

    def get_card(self, event=None):
        if self.player.status == 'take_cards' and self.player.should_take > 0:
            playsound('./resourses/sounds/draw.wav')
            msg = json.dumps({
                'type': 'game_message',
                'message': {
                    'action_type': 'get_card',
                    'sender': self.player.name,
                }
            })
            self.game_socket.send(msg)
            self.player.should_take -= 1
            self.info.set(
                "You should take {} cards".format(
                    self.player.should_take))

        if self.player.status == 'take_cards' and self.player.should_take == 0:
            self.__send_all_taken()

    def __free_user(self):

        self.player.status = 'free'
        self.player.ready['state'] = tk.DISABLED
        self.player.take['state'] = tk.DISABLED

        msg = json.dumps({
            'type': 'game_message',
            'message': {
                'sender': self.player.name,
                'action_type': 'player_free',
                'description': "Player {}  is free".format(
                    self.player.name,
                ),
            }
        })

        self.info.set("Wait end of the game!")
        self.game_socket.send(msg)

    def __reset_all(self):
        self.deck.reset()
        self.player.reset()
        self.table.reset()

    def handle_message(self, msg):
        """
        recieve message from server and make some actions that depends on
        message type.
        """
        msg = msg['message']

        if msg['action_type'] == 'player_addition':

            self.info.set("[{}]:Player {} come in your room!".format(
                msg['time'],
                msg['sender']))

        elif msg['action_type'] == 'users_scores':
            for key in msg['action_info']['scores'].keys():
                if key not in self.score_table.players_scores_tk.keys():
                    self.score_table.addPlayer(key)

            scores = msg['action_info']['scores']
            self.score_table.update(scores)

        elif msg['action_type'] == 'card_addition':
            print('in addition')
            card_type = msg['action_info']['card_type']
            card_value = msg['action_info']['card_value']
            sender_name = msg['sender']

            if self.player.name != sender_name:

                self.table.add_card(card_type, card_value)

            if self.player.status == 'response':
                self.player.take['state'] = tk.ACTIVE
                self.player.ready['state'] = tk.DISABLED
            else:
                self.player.take['state'] = tk.DISABLED
                self.player.ready['state'] = tk.DISABLED

            playsound('./resourses/sounds/draw.wav')

        elif msg['action_type'] == 'players':

            if msg['info']['attack_player'] == self.player.name:
                self.set_atack_player()
            elif msg['info']['response_player'] == self.player.name:
                self.set_response_player()
            else:

                self.set_addition_player()

        elif msg['action_type'] == 'card_response':

            a_card_type = msg['action_info']['a_card_type']
            a_card_value = msg['action_info']['a_card_value']

            r_card_type = msg['action_info']['r_card_type']
            r_card_value = msg['action_info']['r_card_value']

            remain_cards = int(msg['action_info']['remain_cards'])

            r_card = self.deck.create_card(None, (r_card_type, r_card_value))
            a_card = self.table.a_cards[(a_card_type, a_card_value)]

            self.table.response(r_card, a_card)

            if not len(
                    self.table.a_cards) and self.player.status == 'addition':
                self.player.ready['state'] = tk.ACTIVE

            elif not len(self.table.a_cards) and \
                    self.player.status == 'response':
                self.player.take['state'] = tk.DISABLED

            elif self.player.status == 'free' or remain_cards == 0:
                self.ready()

            playsound('./resourses/sounds/draw.wav')

        elif msg['action_type'] == 'player_take':
            playsound('./resourses/sounds/draw.wav')
            self.table.reset()

        elif msg['action_type'] == 'ready':
            self.table.reset()

        elif msg['action_type'] == 'take_cards':
            self.player.ready['state'] = tk.DISABLED
            self.player.take['state'] = tk.DISABLED
            if msg['action_info']['user_name'] == self.player.name:
                if int(msg['action_info']['num_cards']) == 0:
                    self.__send_all_taken()
                else:
                    self.player.status = 'take_cards'
                    self.player.should_take = int(
                        msg['action_info']['num_cards'])
                    self.info.set(
                        "You should take {} cards".format(
                            self.player.should_take))
            else:
                self.info.set(
                    "Wait until {} take cards".format(
                        msg['action_info']['user_name']))

        elif msg['action_type'] == 'get_card':
            card_type = msg['action_info']['card_type']
            card_value = msg['action_info']['card_value']
            deck_size = msg['action_info']['deck_size']
            card = self.deck.create_card(None, (card_type, card_value))
            self.deck.size = deck_size

            self.player.cards.append(card)
            self.deck.update()
            self.player.update()

        elif msg['action_type'] == 'another_user_get':
            playsound('./resourses/sounds/draw.wav')
            self.deck.size = msg['action_info']['deck_size']
            self.deck.update()

        elif msg['action_type'] == 'royal_card':
            self.deck.royal_card = (msg['action_info']['card_type'],
                                    msg['action_info']['card_value'])
            self.__reset_all()
            self.royal_card = self.deck.royal_card
            self.deck.update()

        elif msg['action_type'] == 'empty_deck':
            print('empty_deck')
            self.deck.destroy()

        elif msg['action_type'] == 'user_loose':

            if self.player.name != msg['sender']:
                info_msg = "You win "
                self.table.reset()
            else:
                info_msg = "You loose"

            increase_scores = {}
            for key in self.score_table.players_scores_tk.keys():
                if key == msg['sender']:
                    increase_scores[key] = 0
                else:
                    increase_scores[key] = 1

            self.score_table.update(increase_scores)

            self.info.set(info_msg)

        elif msg['action_type'] == 'drawn':

            self.info.set("Drawn")

        elif msg['action_type'] == 'repeat':
            ask_window = tk.Toplevel(self.player.master)
            ask_window.title("Repeat?")
            text = tk.Label(
                ask_window,
                text="Would you like to continue game?")
            no_btn = tk.Button(ask_window, text='No')
            no_btn['command'] = partial(self.__send_ans, 'no', no_btn)

            yes_btn = tk.Button(ask_window, text='yes')
            yes_btn['command'] = partial(self.__send_ans, 'yes', yes_btn)

            text.grid(row=0, column=0, columnspan=2)
            no_btn.grid(row=1, column=0)
            yes_btn.grid(row=1, column=1)

        elif msg['action_type'] == 'disconnect_message':
            user_name = msg['sender']
            print(self.score_table.players_scores_tk)
            self.score_table.deletePlayer(user_name)
            self.info.set("User {} leave your room! Wait other players...."
                          .format(msg['sender']))
        elif msg['action_type'] == 'connection_closed':
            self.info.set("Problems with connection! Connection_closed!")

    def __send_ans(self, text, btn):
        msg = json.dumps({
            'type': 'game_message',
            'message': {
                'sender': self.player.name,
                'action_type': 'repeat_game',
                'action_info': {
                    'answer': text
                }
            }
        })
        self.game_socket.send(msg)
        if text == 'yes':
            btn['state'] = tk.DISABLED
            btn.master.destroy()
            btn.master.update()

            self.__reset_all()

        else:

            btn['state'] = tk.DISABLED
            self.game_socket.close()
            self.chat_socket.close()
            btn.master.master.master.destroy()
            btn.master.master.master.quit()


class Player(tk.Frame):
    """
    Class that contain players cards
    can do some actions which depeneds on player role
    """

    def __init__(self, parent=None, row=0, name="Unknown", referee=None):

        super().__init__(parent)
        self.place(relx=0.2, rely=0.8)

        self.name = name
        self.referee = referee

        self.cards = []
        self.should_take = 0
        self.status = None
        self.clicked_button = None

        self.visible_cards = tk.Frame(parent)
        self.visible_cards.place(relx=0.2, rely=0.8)

        self.num_visible = 8

        self.left=0
        self.right = self.num_visible

        btn_font = font.Font(family='Helvetica', size=20, weight='bold')

        self.left_button = tk.Button(parent, text="Left",
                                    font=btn_font, command=self.__left)

        self.left_button.place(relx=0.05, rely=0.85)

        self.right_button =  tk.Button(parent, text="Right",
                            font=btn_font, command=self.__right)

        self.right_button.place(relx=0.9, rely=0.85)
        # -----------------------------------------------------------------------
        self.player_buttons = tk.Frame(parent)
        self.player_buttons.place(relx=0.8, rely=0.68)
        self.take = tk.Button(self.player_buttons,
                              text="Take",
                              state=tk.DISABLED,
                              command=self.referee.take)

        self.take.grid(row=0, column=0)
        self.ready = tk.Button(self.player_buttons,
                               text='Ready',
                               state=tk.DISABLED,
                               command=self.referee.ready)
        print('Debug:', self.ready['state'])
        self.ready.grid(row=0, column=1)
        # -----------------------------------------------------------------------


    def __left(self):
        if len(self.cards) > self.num_visible and self.left>0:
            self.left -= 1
            self.right -= 1
            self.update()

    def __right(self):
        if len(self.cards) > self.num_visible and self.right<len(self.cards):
            self.left += 1
            self.right += 1
            self.update()


    def reset(self):
        for card in self.cards:
            card.destroy()

        self.cards = []
        self.should_take = 0
        self.status = None
        self.clicked_button = None
        self.left=0
        self.right = self.num_visible


    def take(self):
        self.referee.take()

    def update(self):
        new_cards = []
        num_cards = len(self.cards)
        if num_cards <= self.num_visible:
            self.left=0
            self.right = self.num_visible

        for idx, card in enumerate(self.cards):

            pc = PlayerCard(self.visible_cards, card.card_id,
                            card.image, idx)
            if idx >= self.left and self.right>=idx:
                print("should show")
                pc.bind('<Button-1>', partial(self.action, pc))
                pc.grid(row=0, column=idx-self.left)

            new_cards.append(pc)
            card.destroy()

        self.cards = new_cards

    def deleteCard(self, card):
        self.cards.pop(card.index)
        card.destroy()
        self.update()

    def __change2cards(self, f_card, s_card):

        index_f, index_s = f_card.index, s_card.index
        card_id_f, card_id_s = f_card.card_id, s_card.card_id
        card_image_f, card_image_s = f_card.image, s_card.image

        f_card.destroy()
        s_card.destroy()

        self.cards[index_f] = Card(None, card_id_s, card_image_s)
        self.cards[index_s] = Card(None, card_id_f, card_image_f)
        self.update()

    def action(self, btn, event=None):

        if self.clicked_button is None and btn in self.cards:
            btn['relief'] = 'sunken'
            self.clicked_button = btn
            if self.status == 'attack':

                self.referee.table['state'] = tk.ACTIVE
                self.referee.table.bind(
                    '<Button-1>',
                    partial(
                        self.action,
                        self.referee.table))

            elif self.status == "response":
                self.referee.make_cards_active()

        else:

            if self.clicked_button in self.cards:
                print("In cards")
                if btn == self.referee.table:
                    print("here")
                    self.referee.add_card_on_table(self.clicked_button)

                elif btn in self.cards:
                    print("change cards")
                    self.__change2cards(btn, self.clicked_button)

                elif btn in self.referee.table.a_cards.values():
                    print("try response")
                    self.referee.response(self.clicked_button, btn)

            self.clicked_button = None


class ScoreTable(tk.Frame):
    """Window for showing players scores."""

    def __init__(self, parent, relx, rely):

        super().__init__(parent)
        self.place(relx=relx, rely=rely)
        self.length = 0
        self.players_scores_tk = {}
        self.players_scores_values = {}

    def addPlayer(self, player_name):
        """When player is connected add it on scrore table."""
        self.players_scores_tk[player_name] = {'frame': tk.Frame(self),
                                               'position': self.length}

        frame = self.players_scores_tk[player_name]['frame']

        frame.grid(row=self.length)

        text_label = tk.Label(frame, text="{} : ".format(player_name),
                              fg="#eee", bg="#333",
                              font="Arial 16")

        text_label.grid(row=0, column=0)

        self.players_scores_values[player_name] = tk.StringVar()
        self.players_scores_values[player_name].set("0")
        score_label = tk.Label(
            frame,
            textvariable=self.players_scores_values[player_name],
            fg="#eee",
            bg="#333",
            font="Arial 16")
        score_label.grid(row=0, column=1)
        self.length += 1

    def deletePlayer(self, player_name):
        """when player is disconnected pop his scores from table."""
        if player_name not in self.players_scores_tk:
            return

        elem = self.players_scores_tk.pop(player_name)
        self.players_scores_values.pop(player_name)
        player_info, player_position = elem['frame'], elem['position']

        player_info.destroy()

        for player_name, elem in self.players_scores_tk.items():
            if elem['position'] > player_position:
                frame = elem['frame']
                frame.grid_forget()
                elem['position'] -= 1
                frame.grid(row=elem['position'])
        self.length -= 1

    def update(self, users_scores):
        for user_name, value in users_scores.items():

            self.players_scores_values[user_name].set(value)
