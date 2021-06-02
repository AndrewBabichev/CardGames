"""Module for queen card game."""

import numpy as np
import tkinter as tk
import os

from functools import partial
from tkinter import messagebox
from .cards import Hand, Deck
from os.path import join

try:
    from playsound import playsound
except ImportError:
    def playsound(filename):
        """Empty functions if import fails."""
        pass

RESOURSES_DIR = os.path.join(os.path.dirname(__file__), "..", 'resources')


class Queen_Hand(Hand):
    """Extended hand class with queen game features.

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
        super().__init__(parent, row, show_cards, allow_movement)

    def choose_card(self, index, event=None):
        """
        Either discard same values cards or perform base class actions.

        :param index: index to hand`s card to perform action on
        :type index: int
        """
        card_id_1, card_id_2 = \
            self.cards_ids[index], self.cards_ids[self.change_index]
        if (self.change_index != -1 and
                card_id_1 != card_id_2 and card_id_1[1] == card_id_2[1] and
                card_id_1 != [3, 11] and card_id_2 != [3, 11]):

            playsound(join(RESOURSES_DIR, 'sounds/Passturn.wav'))
            self.cards_ids.pop(max(index, self.change_index))
            self.cards_ids.pop(min(index, self.change_index))
            self.show(self.cards_ids)
            self.change_index = -1
        else:
            super().choose_card(index)


class Queen(Deck):
    """Handler for queen game.

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
            hands=None, player_hand=0, expand=True):
        """Initialize queen params and start new game."""
        super().__init__(parent, row, hands, player_hand, expand)

        self.ready_button = tk.Button(
            parent,
            text=_("Ready"),
            font=40,
            command=self.pass_turn
        )
        self.ready_button.place(y=row * self.card_height + 90, x=800)
        self.new_game()

    def unfold(self, index, event=None):
        """
        Unfold chosen card and place it to player hand.

        :param index: index to chosen card
        :type index: int
        """
        if self.stage == 0:
            playsound(join(RESOURSES_DIR, 'sounds/untap.wav'))
            position = self.hands[self.enemy_hand].position(index)
            card_id = self.hands[self.enemy_hand].cards_ids.pop(index)
            self.hands[self.enemy_hand].cards[index].destroy()
            self.hands[self.enemy_hand].cards[index] = self.create_button(
                card_id,
                position
            )
            self.hands[self.player_hand].cards_ids.append(card_id)
            self.stage = 1
            self.master.after(200, self.unfold, -1)
        elif self.stage == 1:
            for hand in self.hands:
                hand.show(hand.cards_ids)
            for i, card in enumerate(self.hands[self.enemy_hand].cards):
                card.bind('<Button-1>', partial(self.unfold, i))
            self.end_game(2)

    def _find_pairs(self, hand):
        """
        Find indices of cards with same values.

        :param hand: card hand to perform search on
        :return: founded indices or -1 if there are no pairs
        :rtype: tuple
        """
        for i in range(len(hand.cards_ids)):
            for j in range(i + 1, len(hand.cards_ids)):
                card_id_1, card_id_2 = \
                    hand.cards_ids[i], hand.cards_ids[j]
                if (card_id_1[1] == card_id_2[1] and
                        card_id_1 != [3, 11] and card_id_2 != [3, 11]):
                    return max(i, j), min(i, j)
        return -1

    def remove_pairs(self, hand):
        """
        Remove all card pairs with same values except for queen of spades.

        :param hand: card hand to remove cards from
        """
        flag = self._find_pairs(hand)
        if flag != -1:
            playsound(join(RESOURSES_DIR, 'sounds/Passturn.wav'))
        while flag != -1:
            hand.cards_ids.pop(flag[0])
            hand.cards_ids.pop(flag[1])
            flag = self._find_pairs(hand)

    def end_game(self, stage=0):
        """
        Check if game is finished otherwise set game stage.

        :param stage: stage to set after function, defaults to 0
        :type stage: int
        """
        if len(self.hands[self.player_hand].cards_ids) == 0:
            messagebox.showinfo(message=_("Win"))
            self.new_game()
        else:
            enemy_hands = list()
            for enemy_hand in self.enemy_hands:
                hand = self.hands[enemy_hand]
                if len(hand.cards_ids) > 0:
                    enemy_hands.append(enemy_hand)
            self.enemy_hands = enemy_hands
            if (len(self.enemy_hands) == 0):
                messagebox.showinfo(message=_("Lose"))
                self.new_game()
            else:
                self.enemy_hand = self.enemy_hands[-1]
                for i, card in enumerate(self.hands[self.enemy_hand].cards):
                    card.bind('<Button-1>', partial(self.unfold, i))
                    self.stage = stage

    def pass_turn(self, event=None):
        """
        Pass the turn to the counterpart.

        Opponent draws card, removes pairs and passes turn
        """
        self.end_game(stage=2)
        if self.stage == 2:
            self.draw_list = []
            for i in range(len(self.enemy_hands) - 1):
                self.draw_list.append(
                    [self.enemy_hands[i], self.enemy_hands[i+1]]
                )
            self.draw_list.append([self.player_hand, self.enemy_hands[0]])
            for i, indices in enumerate(self.draw_list):
                self.master.after(
                    2000 * i,
                    self.draw_from_hand,
                    indices[0],
                    indices[1]
                )
            self.master.after((i + 1) * 2000, self.end_game)

    def draw_from_hand(self, index_draw, index_hold):
        """
        Start card draw.

        :param index_draw: index to hand to draw from
        :type index_draw: int
        :param index_hold: index to hand to draw to
        :type index_hold: int
        """
        hand_draw = self.hands[index_draw]
        hand_hold = self.hands[index_hold]
        if len(hand_hold.cards_ids) > 0:
            if self.stage == 2:
                index = np.random.choice(
                    np.arange(len(hand_draw.cards_ids)), 1)[0]
                card_id = hand_draw.cards_ids[index]
                hand_draw.cards_ids[index] = None

                hand_hold.cards_ids.append(card_id)
                position = hand_hold.position(len(hand_hold.cards_ids) - 1)
                hand_hold.show(hand_hold.cards_ids)
                hand_draw.show(hand_draw.cards_ids)
                hand_hold.cards[-1].destroy()
                hand_hold.cards[-1] = self.create_button(
                    card_id,
                    position
                )
                self.stage = 3
                self.master.after(
                    500,
                    self.draw_from_hand,
                    index_draw,
                    index_hold,
                )
            elif self.stage == 3:
                index = hand_draw.cards_ids.index(None)
                hand_draw.cards_ids.pop(index)
                self.remove_pairs(hand_hold)
                np.random.shuffle(hand_hold.cards_ids)
                hand_hold.show(hand_hold.cards_ids)
                hand_draw.show(hand_draw.cards_ids)
                self.stage = 2

    def new_game(self):
        """Reset game parameters and draw hand`s cards."""
        self.enemy_hands = list(np.delete(np.arange(len(self.hands)), 2))
        self.enemy_hand = self.enemy_hands[-1]
        self.shuffle()
        self.deck_cards_ids = np.delete(self.deck_cards_ids, 37)
        for hand, amount in zip(self.hands, [17, 17, 17]):
            self.draw(hand, amount, drop=True)
            self.remove_pairs(hand)
            hand.show(hand.cards_ids)

        self.end_game(0)
