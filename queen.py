import numpy as np
import tkinter as tk

from functools import partial
from tkinter import messagebox

from cards import *


class Queen_Hand(Hand):
    def __init__(self, parent = None, row = 0, show_cards = True, allow_movement = True):
        super().__init__(parent, row, show_cards, allow_movement)

    def choose_card(self, index, event):
        if (self.change_index != -1 and self.cards_ids[index] != self.cards_ids[self.change_index] and
            self.cards_ids[index][1] == self.cards_ids[self.change_index][1] and
            self.cards_ids[index] != [3, 11] and self.cards_ids[self.change_index] != [3, 11]):

            playsound('./resourses/sounds/Passturn.wav')
            self.cards_ids.pop(max(index, self.change_index))
            self.cards_ids.pop(min(index, self.change_index))
            self.show(self.cards_ids)
            self.change_index = -1
            if len(self.cards_ids) == 0:
                messagebox.showinfo(message = "Win")
                Q.master.after(200, Q.new_game())
        else:
            super().choose_card(index, None)

class Queen(Deck):
    def __init__(self, parent = None, row = 0, hands = None, player_hand = 0, expand = True):

        super().__init__(parent, row, hands, player_hand, expand)
        self.enemy_hand = 1 - self.player_hand

        self.ready_button = tk.Button(parent, text = 'Ready', font = 40, command = self.pass_turn)
        self.ready_button.place(y = row * self.card_height + 90, x = 800)

        self.new_game()

    def unfold(self, index = None, event = None):
        if self.stage == 0:
            playsound('./resourses/sounds/untap.wav')
            position = self.hands[self.enemy_hand].position(index)
            card_id = self.hands[self.enemy_hand].cards_ids.pop(index)
            if len(self.hands[self.enemy_hand].cards_ids) == 0:
                messagebox.showinfo(message = "Lose")
                self.new_game()
            else:
                self.hands[self.enemy_hand].cards[index].destroy()
                self.hands[self.enemy_hand].cards[index] = self.create_button(card_id, position)
                self.hands[self.player_hand].cards_ids.append(card_id)
                self.stage = 1

                self.master.after(200, self.unfold)
        elif self.stage == 1:
            for hand in self.hands:
                hand.show(hand.cards_ids)
            for i, card in enumerate(self.hands[self.enemy_hand].cards):
                card.bind('<Button-1>', partial(self.unfold, i))
            self.stage = 2

    def find_pairs(self, hand):
        for i in range(len(hand.cards_ids)):
            for j in range(i + 1, len(hand.cards_ids)):
                if hand.cards_ids[i][1] == hand.cards_ids[j][1] and hand.cards_ids[i] != [3, 11] and hand.cards_ids[j] != [3, 11]:
                    return max(i, j), min(i, j)
        return -1

    def remove_pairs(self, hand):
        flag = self.find_pairs(hand)
        if flag != -1:
            playsound('./resourses/sounds/Passturn.wav')
        while flag != -1:
            hand.cards_ids.pop(flag[0])
            hand.cards_ids.pop(flag[1])
            flag = self.find_pairs(hand)

    def pass_turn(self, event = None):
        if self.stage == 2:
            index = np.random.choice(np.arange(len(self.hands[self.player_hand].cards_ids)), 1)[0]
            card_id = self.hands[self.player_hand].cards_ids[index]
            self.hands[self.player_hand].cards_ids[index] = None

            self.hands[self.enemy_hand].cards_ids.append(card_id)
            position = self.hands[self.enemy_hand].position(len(self.hands[self.enemy_hand].cards_ids) - 1)
            for hand in self.hands:
                hand.show(hand.cards_ids)
            self.hands[self.enemy_hand].cards[-1].destroy()
            self.hands[self.enemy_hand].cards[-1] = self.create_button(card_id, position)
            self.stage = 3
            self.master.after(500, self.pass_turn)
        elif self.stage == 3:
            index = self.hands[self.player_hand].cards_ids.index(None)
            self.hands[self.player_hand].cards_ids.pop(index)
            self.remove_pairs(self.hands[self.enemy_hand])
            np.random.shuffle(self.hands[self.enemy_hand].cards_ids)
            for hand in self.hands:
                hand.show(hand.cards_ids)
            for i, card in enumerate(self.hands[self.enemy_hand].cards):
                card.bind('<Button-1>', partial(self.unfold, i))
            self.stage = 0
            if (len(self.hands[self.enemy_hand].cards_ids) == 0):
                messagebox.showinfo(message = "Lose")
                self.new_game()
            elif (len(self.hands[self.player_hand].cards_ids) == 0):
                messagebox.showinfo(message = "Win")
                self.new_game()
            print(len(self.hands[self.enemy_hand].cards_ids), len(self.hands[self.player_hand].cards_ids))


    def new_game(self):
        self.stage = 0
        self.shuffle()
        self.deck_cards_ids = np.delete(self.deck_cards_ids, 37) #queen of clubs
        self.draw(self.hands[self.enemy_hand], 25, drop = True)
        self.remove_pairs(self.hands[self.enemy_hand])
        self.hands[self.enemy_hand].show(self.hands[self.enemy_hand].cards_ids)
        self.draw(self.hands[self.player_hand], 26, drop = True)
        self.remove_pairs(self.hands[self.player_hand])
        self.hands[self.player_hand].show(self.hands[self.player_hand].cards_ids)
        for i, card in enumerate(self.hands[self.enemy_hand].cards):
            card.bind('<Button-1>', partial(self.unfold, i))

if __name__ == '__main__':

    root = tk.Tk()
    root.geometry('870x670')

    H1 = Queen_Hand(root, row = 0, show_cards = False, allow_movement = False)
    H1.show([])

    H2 = Queen_Hand(root, row = 2, show_cards = True, allow_movement = True)
    H2.show([])

    Q = Queen(root, row = 1, hands = [H1, H2], player_hand = 1)
    root.mainloop()
