"""Module for common card entities and operations."""

import numpy as np
import tkinter as tk
import os

from functools import partial
from os.path import join


RESOURSES_DIR = os.path.join(os.path.dirname(__file__), "..", 'resources')

try:
    from playsound import playsound
    playsound(join(RESOURSES_DIR, 'sounds/shuffle.wav'))
except ImportError:
    def playsound(filename):
        """Empty functions if import fails."""
        pass


class Cards(tk.Frame):
    """Class for basic operation with cards.

    :param parent: parameter to be passed to tkinter.Frame constructor,
        defaults to None
    """

    def __init__(self, parent=None):
        """Initialize all card`s images."""
        super().__init__(parent)
        # 0 - Hearts, 1 - Diamonds, 2 - Clubs, 3 - Spades
        self.cards_images = np.zeros((4, 13), dtype=tk.PhotoImage)
        self.card_height, self.card_width = 230, 145

        for i in range(self.cards_images.shape[0]):
            for j in range(self.cards_images.shape[1]):
                name = join(RESOURSES_DIR, 'cards', '{}_{}.png'.format(i, j))
                self.cards_images[i, j] = tk.PhotoImage(file=name)
        self.empty_image = tk.PhotoImage(
            file=join(RESOURSES_DIR, 'cards/empty.png'))
        self.back_image = tk.PhotoImage(
            file=join(RESOURSES_DIR, 'cards/back.png'))

    def create_button(self, card_id, position, relief='groove'):
        """
        Create specified card`s button in specified position.

        :param card_id: id of card to create; could be either list
            [card_suit, card_value] or -1 for blank space or
            None for back of cards
        :param position: desired y coordinate and x coordinate for button
        :type position: list
        :param relief: relief style for button, defaults to groove
        :type relief: string
        :return: created button
        :rtype: tkinter.Button
        """
        if card_id is None:
            button = tk.Button(
                self.master,
                image=self.empty_image,
                relief=relief
            )
        elif card_id == -1:
            button = tk.Button(
                self.master,
                image=self.back_image,
                relief=relief
            )
        else:
            (i, j) = card_id
            button = tk.Button(
                self.master,
                image=self.cards_images[i, j],
                relief=relief
            )
        button.place(y=position[0], x=position[1])
        return button


class Deck(Cards):
    """Base class for game handlers.

    :param parent: parameter to be passed to tkinter.Frame constructor,
        defaults to None
    :param row: row to visualize deck on, defaults to 0
    :type row: int
    :param hands: card hands to handle, defaults to None
    :param player_hand: index to player hand, defaults to 0
    :type player_hand: int
    :param expand: whether to expand card hand or to keep it to 6 cards,
        defaults to False
    :type expand: bool
    """

    def __init__(
            self, parent=None, row=0,
            hands=None, player_hand=0, expand=False):
        """Create card deck and initialize common game parameters."""
        super().__init__(parent)
        self.row = row
        self.hands = hands
        self.player_hand = player_hand
        self.expand = expand

        self.deck_cards_ids = np.arange(52)
        self.deck_cards = []
        self.update()

    def update(self):
        """Update and visualize deck cards."""
        for deck_card in self.deck_cards:
            deck_card.destroy()

        self.deck_cards.clear()
        self.deck_cards.append(
            tk.Button(self.master, image=self.empty_image, state='disabled')
        )
        self.deck_cards[-1].place(
            y=self.row * self.card_height,
            x=0
        )
        self.deck_cards[-1].bind(
            '<Button-3>',
            partial(self.get, self.hands[self.player_hand])
        )

        for i in range(int(np.ceil(self.deck_cards_ids.size / 13))):
            self.deck_cards.append(
                tk.Button(self.master, image=self.back_image, state='disabled')
            )
            self.deck_cards[-1].place(
                y=self.row * self.card_height - i*3,
                x=-i*3
            )
            self.deck_cards[-1].bind(
                '<Button-3>',
                partial(self.get, self.hands[self.player_hand])
            )

    def draw(self, hand, amount=6, empty=0, drop=False, event=None):
        """
        Draw desired amount of cards to specified hand and visualize them.

        :param hands: card hands to handle
        :param amount: total amount of cards to draw, defaults to 6
        :type amount: int
        :param empty: number of drawed card to be empty, defaults to 0
        :type empty: int
        :param drop: whether to return drawed cards to deck or not,
            defaults to False
        :type drop: bool
        """
        if self.deck_cards_ids.size > 0:
            playsound(join(RESOURSES_DIR, 'sounds/draw.wav'))
            cards_ids = []
            for i in range(amount - empty):
                card_id = np.random.choice(self.deck_cards_ids, (1))
                if drop:
                    self.deck_cards_ids = np.setdiff1d(
                        self.deck_cards_ids,
                        card_id
                    )
                cards_ids.append([card_id[0] // 13, card_id[0] % 13])

            for i in range(empty):
                cards_ids.append(None)
            hand.show(cards_ids)
            self.update()

    def get(self, hand, event=None, card_id=None):
        """
        Draw one card to specified hand and visualize it.

        :param hand: card hand to draw to
        :param card_id: card_id to get, defaults to None
        :type card_id: list
        """
        if None in hand.cards_ids and self.deck_cards_ids.size > 0:
            playsound(join(RESOURSES_DIR, 'sounds/draw.wav'))
            index = hand.cards_ids.index(None)
            if card_id is None:
                card_id = np.random.choice(self.deck_cards_ids, (1))
            self.deck_cards_ids = np.setdiff1d(self.deck_cards_ids, card_id)

            i, j = card_id[0] // 13, card_id[0] % 13
            hand.cards_ids[index] = [i, j]
            hand.show(hand.cards_ids)
            self.update()

        elif self.expand and self.deck_cards_ids.size > 0:
            playsound(join(RESOURSES_DIR, 'sounds/draw.wav'))
            if card_id is None:
                card_id = np.random.choice(self.deck_cards_ids, (1))
            self.deck_cards_ids = np.setdiff1d(self.deck_cards_ids, card_id)

            i, j = card_id[0] // 13, card_id[0] % 13
            hand.cards_ids.append([i, j])
            hand.show(hand.cards_ids)
            self.update()

    def shuffle(self, event=None):
        """Reset the deck and card hands."""
        playsound(join(RESOURSES_DIR, 'sounds/shuffle.wav'))
        self.deck_cards_ids = np.arange(52)
        self.update()

        for hand in self.hands:
            hand.show([None, None, None, None, None, None])


class Hand(Cards):
    """Class that simulates actions of a card hand.

    :param parent: parameter to be passed to tkinter.Frame constructor,
        defaults to None
    :param row: row to visualize hand on, defaults to 0
    :type row: int
    :param show_cards: whether to show cards or their backs, defaults to True
    :type show_cards: bool
    :param allow_movement: whether to allow to move cards within the hand,
        defaults to True
    :type allow_movement: bool
    """

    def __init__(
            self, parent=None, row=0,
            show_cards=True, allow_movement=True):
        """Initialize card hand parameters."""
        super().__init__(parent)
        self.row = row
        self.show_cards = show_cards
        self.allow_movement = allow_movement

        self.cards_ids = []
        self.cards = []
        self.change_index = -1

    def position(self, column):
        """
        Return card`s position based on its column.

        :param column: desired place in card hand (0 .. len(cards_ids) - 1)
        :type column: int
        """
        if len(self.cards_ids) <= 6:
            return [self.row * self.card_height, column * self.card_width]
        else:
            return [self.row * self.card_height, np.floor(
                column * self.card_width * 5 / (len(self.cards_ids) - 1))
            ]

    def choose_card(self, index, event=None):
        """
        Highlight or swap specified card.

        :param index: index to hand`s card to perform action on
        :type index: int
        """
        if self.change_index == -1:
            self.cards[index].destroy()
            self.cards[index] = self.create_button(
                self.cards_ids[index],
                self.position(index),
                'sunken'
            )
            self.cards[index].bind(
                '<Button-1>',
                partial(self.choose_card, index)
            )
            self.change_index = index
        else:
            if self.change_index != index:
                playsound(join(RESOURSES_DIR, 'sounds/playcard.wav'))
                self.cards_ids[index], self.cards_ids[self.change_index] = \
                    self.cards_ids[self.change_index], self.cards_ids[index]
                self.show(self.cards_ids)
            else:
                self.show(self.cards_ids)

            self.change_index = -1

    def show(self, cards_ids):
        """
        Visualize specified cards.

        :param cards_ids: card`s identifiers to visualize
        :type cards_ids: list
        """
        for card in self.cards:
            card.destroy()
        self.cards.clear()

        self.cards_ids = cards_ids

        if len(cards_ids) != 0:
            for column, card_id in enumerate(cards_ids):
                if not self.show_cards and card_id is not None:
                    self.cards.append(
                        self.create_button(-1, self.position(column))
                    )
                else:
                    self.cards.append(
                        self.create_button(card_id, self.position(column))
                    )
                if self.allow_movement:
                    self.cards[-1].bind(
                        '<Button-1>',
                        partial(self.choose_card, column)
                    )
