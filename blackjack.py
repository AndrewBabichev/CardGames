import numpy as np
import tkinter as tk

from functools import partial
from tkinter import messagebox

from cards import Deck, Hand, Cards

class Blackjack(Deck):
    def __init__(self, parent = None, row = 0, hands = None, player_hand = 0):

        self.player_hand = player_hand
        self.enemy_hand = 1 - self.player_hand

        self.enemy_score_button = tk.Button(parent, text = '0', font = 40)
        self.player_score_button = tk.Button(parent, text = '0', font = 40)

        super().__init__(parent, row, hands, player_hand)
        self.stage = 0

        self.value = {0:11, 1:2, 2:3, 3:4, 4:5, 5:6, 6:7, 7:8, 8:9, 9:10, 10:2, 11:3, 12:4}
        self.stand_button = tk.Button(parent, text = 'Stand', font = 40, command = self.end_game)

        self.enemy_score_button.place(y = row * self.card_height + 50, x = 818)
        self.stand_button.place(y = row * self.card_height + 90, x = 800)
        self.player_score_button.place(y = row * self.card_height + 130, x = 818)


        self.new_game()


    def end_game(self, event = None):
        self.enemy_score, enemy_cards_amount = self.count_score(self.hands[self.enemy_hand])
        self.player_score, _ = self.count_score(self.hands[self.player_hand])
        if self.player_score > 21:
            messagebox.showinfo(message = "Lose")
            self.new_game()
        else:
            if self.enemy_score < self.player_score and self.enemy_score <= 21 and enemy_cards_amount <= 6:
                self.get(self.hands[self.enemy_hand])
                self.enemy_score, enemy_cards_amount = self.count_score(self.hands[self.enemy_hand])
                self.master.after(100, self.end_game)
            else:
                if self.player_score > self.enemy_score or self.enemy_score > 21:
                    messagebox.showinfo(message = "Win")
                elif self.player_score == self.enemy_score:
                    messagebox.showinfo(message = "Draw")
                else:
                    messagebox.showinfo(message = "Lose")
                self.new_game()

    def new_game(self):
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

    def count_score(self, hand):
        score, amount = 0, 0
        for card_id in hand.cards_ids:
            if card_id is not None:
                score += self.value[card_id[1]]
                amount += 1
        return score, amount

    def update(self):
        super().update()
        self.enemy_score, _ = self.count_score(self.hands[self.enemy_hand])
        self.enemy_score_button.configure(text = str(self.enemy_score))
        self.player_score, _ = self.count_score(self.hands[self.player_hand])
        self.player_score_button.configure(text = str(self.player_score))
