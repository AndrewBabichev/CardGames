"""Module for blackjack card game."""

import tkinter as tk

from cards import Deck
from tkinter import messagebox


class Blackjack(Deck):
    """Handler for blackjack game."""

    def __init__(
            self, parent=None, row=0,
            hands=None, player_hand=0, expand=False):
        """
        Create deck and game buttons, initialize bj params and start new game.

        Args:
            parent: parameter to be passed to tkinter.Frame constructor
            row: row to visualize deck on
            hands: card hands to handle
            player_hand: index to player hand
            expand: whether to expand card hand or to keep it to 6 cards
        """
        self.player_hand = player_hand
        self.enemy_hand = 1 - self.player_hand
        self.enemy_score_button = tk.Button(parent, text='0', font=40)
        self.player_score_button = tk.Button(parent, text='0', font=40)
        super().__init__(parent, row, hands, player_hand)

        self.parent = parent
        self.stage = 0

        self.value = {
            0: 11, 1: 2, 2: 3, 3: 4,
            4: 5, 5: 6, 6: 7, 7: 8, 8: 9,
            9: 10, 10: 2, 11: 3, 12: 4
        }
        self.stand_button = tk.Button(
            parent,
            text='Stand',
            font=40,
            command=self.end_game
        )

        self.enemy_score_button.place(y=row * self.card_height + 50, x=818)
        self.stand_button.place(y=row * self.card_height + 90, x=800)
        self.player_score_button.place(y=row * self.card_height + 130, x=818)
        self.new_game()

    def end_game(self, event=None):
        """Finish computer`s turn, determine the winner and start new game."""
        self.enemy_score, enemy_cards_amount = self._count_score(
            self.hands[self.enemy_hand]
        )
        self.player_score, _ = self._count_score(self.hands[self.player_hand])
        if self.player_score > 21:
            messagebox.showinfo(message="Lose")
            self.new_game()
        else:
            if (self.enemy_score < self.player_score and
                    self.enemy_score < 21 and enemy_cards_amount < 6):

                self.get(self.hands[self.enemy_hand])

                self.enemy_score, _ = self._count_score(
                    self.hands[self.enemy_hand]
                )
                self.master.after(100, self.end_game)
            else:
                if (self.player_score > self.enemy_score or
                        self.enemy_score > 21):
                    messagebox.showinfo(message="Win")
                elif self.player_score == self.enemy_score:
                    messagebox.showinfo(message="Draw")
                else:
                    messagebox.showinfo(message="Lose")
                self.new_game()

    def new_game(self):
        """Reset game parameters and smoothly draw hand`s cards."""
        if self.stage == 0:
            self.shuffle()
            self.stage = 1

            self.master.after(100, self.new_game)
        elif self.stage == 1:
            self.get(self.hands[self.enemy_hand])
            self.stage = 2
            self.master.after(100, self.new_game)
        elif self.stage == 2:
            self.get(self.hands[self.player_hand])
            self.stage = 3

            self.master.after(100, self.new_game)

        elif self.stage == 3:
            self.get(self.hands[self.enemy_hand])
            self.stage = 4

            self.master.after(100, self.new_game)
        elif self.stage == 4:
            self.get(self.hands[self.player_hand])
            self.stage = 0

    def _count_score(self, hand):
        """
        Compute hand`s cards value.

        Args:
            hand: card hand to compute score

        Returns:
            int: computed hand score

        """
        score, amount = 0, 0
        for card_id in hand.cards_ids:
            if card_id is not None:
                score += self.value[card_id[1]]
                amount += 1
        return score, amount

    def update(self):
        """Update and visualize deck cards and game buttons."""
        super().update()

        self.enemy_score, _ = self._count_score(self.hands[self.enemy_hand])
        self.enemy_score_button.configure(text=str(self.enemy_score))
        self.player_score, _ = self._count_score(self.hands[self.player_hand])
        self.player_score_button.configure(text=str(self.player_score))

