from skimage.io import imread
import matplotlib.pyplot as plt
import tkinter as tk
import numpy as np
from functools import partial
import glob
from playsound import playsound
import time

class Cards(tk.Frame):
    def __init__(self, parent = None):
        super().__init__(parent)
        self.cards_images = np.zeros((4, 13), dtype = tk.PhotoImage) #0 - Hearts (Черви), 1 - Diamonds (Буби), 2 - Clubs (Крести), 3 - Spades (Пики)

        for i in range(self.cards_images.shape[0]):
            for j in range(self.cards_images.shape[1]):
                name = './resourses/cards/' + str(i) + '_' + str(j) + '.png'
                self.cards_images[i, j] = tk.PhotoImage(file = name)
        self.empty_image = tk.PhotoImage(file = './resourses/cards/empty.png')
        self.back_image = tk.PhotoImage(file = './resourses/cards/back.png')

    def create_button(self, cards_id, index, position, relief = 'groove'):
        if cards_id != None:
            (i, j) = cards_id
            button = tk.Button(self.master, relief = relief, image = self.cards_images[i, j])
        else:
            button = tk.Button(self.master, relief = relief, image = self.empty_image, state = tk.DISABLED)
        button.place(y = position[0], x = position[1])
        return button

class Deck(Cards):
    def __init__(self, parent = None, row = 0, hands = None, player_hand = 0):
        super().__init__(parent)
        self.row = row
        self.hands = hands
        self.player_hand = player_hand

        self.deck_cards_ids = np.arange(52)
        self.deck_cards = []
        self.cards = []
        self.update()


    def update(self):
        for deck_card in self.deck_cards:
            deck_card.destroy()

        self.deck_cards = []
        self.deck_cards.append(tk.Button(self.master, image = self.empty_image))
        self.deck_cards[-1].place(y = self.row * 230, x = 0)
        self.deck_cards[-1].bind('<Button-1>', partial(self.draw, self.hands[self.player_hand], 6, 5, True))
        self.deck_cards[-1].bind('<Button-2>', self.shuffle)
        self.deck_cards[-1].bind('<Button-3>', partial(self.get, self.hands[self.player_hand]))

        for i in range(int(np.ceil(self.deck_cards_ids.size / 13))):
            self.deck_cards.append(tk.Button(self.master, image = self.back_image, state = tk.DISABLED))
            self.deck_cards[-1].place(y = self.row * 230 - i*3, x = -i*3)
            self.deck_cards[-1].bind('<Button-1>', partial(self.draw, self.hands[self.player_hand], 6, 5, True))
            self.deck_cards[-1].bind('<Button-2>', self.shuffle)
            self.deck_cards[-1].bind('<Button-3>', partial(self.get, self.hands[self.player_hand]))

    def draw(self, hand, amount = 6, empty = 0, drop = False, event = None):
        if self.deck_cards_ids.size > 0:
            cards_id = []
            for i in range(amount - empty):
                card_id = np.random.choice(self.deck_cards_ids, (1))
                if drop:
                    self.deck_cards_ids = np.setdiff1d(self.deck_cards_ids, card_id)
                cards_id.append([card_id[0] // 13, card_id[0] % 13])
                playsound('./resourses/sounds/draw.wav')

            for i in range(empty):
                cards_id.append(None)
            hand.show(cards_id)

            self.update()

    def get(self, hand, event = None):
        if None in hand.cards_ids and self.deck_cards_ids.size > 0:
            playsound('./resourses/sounds/draw.wav')
            index = hand.cards_ids.index(None)
            card_id = np.random.choice(self.deck_cards_ids, (1))
            self.deck_cards_ids = np.setdiff1d(self.deck_cards_ids, card_id)
            i, j = card_id[0] // 13, card_id[0] % 13
            hand.cards_ids[index] = [i, j]
            hand.show(hand.cards_ids)
            self.update()

    def shuffle(self, event = None):
        playsound('./resourses/sounds/shuffle.wav')
        self.deck_cards_ids = np.arange(52)
        self.update()

        for hand in self.hands:
            hand.show([None, None, None, None, None, None])


class Hand(Cards):
    def __init__(self, parent = None, row = 0):
        super().__init__(parent)
        self.cards_ids = []
        self.cards = []
        self.positions = []
        self.row = row
        self.change = -1

    def choose_card(self, index, event):
        if self.change == -1:
            self.change = index
            self.cards[index] = self.create_button(self.cards_ids[index], index, self.positions[index], 'sunken')
            self.cards[index].bind('<Button-1>', partial(self.choose_card, index))
        else:
            if self.change != index:
                playsound('./resourses/sounds/playcard.wav')
                self.cards_ids[index], self.cards_ids[self.change] = self.cards_ids[self.change], self.cards_ids[index]

                self.cards[index].destroy(), self.cards[self.change].destroy()
                self.cards[index] = self.create_button(self.cards_ids[index], index, self.positions[index])
                self.cards[index].bind('<Button-1>', partial(self.choose_card, index))
                self.cards[self.change] = self.create_button(self.cards_ids[self.change], self.change, self.positions[self.change])
                self.cards[self.change].bind('<Button-1>', partial(self.choose_card, self.change))
            else:
                self.cards[index] = self.create_button(self.cards_ids[index], index, self.positions[index])
                self.cards[index].bind('<Button-1>', partial(self.choose_card, index))

            self.change = -1

    def show(self, cards_ids):
        if len(self.cards_ids) != 0:
            for card in self.cards:
                card.destroy()
            self.cards, self.positions = list(), list()

        if len(cards_ids) != 0:
            for column, cards_id in enumerate(cards_ids):
                self.positions.append( [self.row * 230, column * 145] )
                self.cards.append(self.create_button(cards_id, column, self.positions[column]))
                self.cards[-1].bind('<Button-1>', partial(self.choose_card, column))

        self.cards_ids = cards_ids



"""root = tk.Tk()
root.geometry('870x670')




H1 = Hand(root, 0)
H1.show([None, None, None, None, None, None])

H3 = Hand(root, 2)

D = Deck(root, row = 1, hands = [H1, H3], player_hand = 1)
#D.draw(D.hands[0], 5)
H3.show([None, None, None, None, None, None])


root.mainloop()"""
