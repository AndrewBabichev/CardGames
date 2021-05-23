import tkinter as tk

import numpy as np

from tkinter import *
from blackjack import *
from FoolOnline import *
from queen import *
from cards import *

from functools import partial

class MainMenu(tk.Frame):

    def __init__(self, master, apps, apps_names):
        assert len(apps) == len(apps_names)

        self.apps = apps
        self.apps_names = apps_names

        tk.Frame.__init__(self, master)

        self.grid(sticky=tk.N+tk.E+tk.S+tk.W)
        top=self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        self.rowconfigure(tuple((i for i in range(len(apps_names)))),  weight=1)


        self.quitButton = tk.Button(self, text='Exit',
                                    font=('Helvetica', 16),
                                    command=self.quit)
        self.quitButton.grid(row=len(apps_names), padx=10,
                            pady=20, sticky="NSEW")

        self.game_buttons = []
        for idx in range(len(apps)):

            closure = partial(self.apps[idx], self)

            btn = tk.Button(self, text=self.apps_names[idx],
                                        font=('Helvetica', 16),
                                        command=closure)

            btn.grid(row=idx, padx=10, pady=20, sticky='NSEW')

    def change_frame(self, fr):

        fr.reset()
        fr.tkraise()


def init_bj(root):


    #root.master.withdraw()
    root = Toplevel(root)
    root.geometry('1000x900')


    H1 = Hand(root, 0)
    H1.show([None, None, None, None, None, None])

    H2 = Hand(root, 2)
    H2.show([None, None, None, None, None, None])

    B = Blackjack(root, row = 1, hands = [H1, H2], player_hand = 1)



def find_gamers(root):

    m = Main(root)
    #m.mainloop()
    #root.destroy()



def queen(root):

    pass 
    '''
    root = Toplevel(root)
    root.geometry('870x900')

    H1 = Queen_Hand(root, row=0, show_cards=False, allow_movement=False)

    H2 = Queen_Hand(root, row=1, show_cards=False, allow_movement=False)

    H3 = Queen_Hand(root, row=3, show_cards=True, allow_movement=True)

    Q = Queen(root, row=2, hands=[H1, H2, H3], player_hand=2)
    #root.mainloop()
    '''
if __name__ == '__main__':


    root = tk.Tk()

    root.title('Cards Games')
    root.geometry('300x500')
    tmp_names = ['Blackjack', 'Fool-online', 'Queen']
    app_frames = [init_bj, find_gamers, Queen]


    buttons_frame = tk.LabelFrame(  root, text="Games",
                                    height=500, width=300,
                                    labelanchor='n')

    buttons_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    menu = MainMenu(buttons_frame, app_frames, tmp_names)

    root.mainloop()
