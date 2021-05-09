import tkinter as tk

import numpy as np

from tkinter import *
from blackjack import *
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

            closure = partial(self.apps[idx], self) #fantastic

            btn = tk.Button(self, text=self.apps_names[idx],
                                        font=('Helvetica', 16),
                                        command=closure)

            btn.grid(row=idx, padx=10, pady=20, sticky='NSEW')

    def change_frame(self, fr):

        fr.reset()
        fr.tkraise()


def init_bj(root):



    root = Toplevel(root)
    root.geometry('1000x900')


    H1 = Hand(root, 0)
    H1.show([None, None, None, None, None, None])

    H2 = Hand(root, 2)
    H2.show([None, None, None, None, None, None])

    B = Blackjack(root, row = 1, hands = [H1, H2], player_hand = 1)



def find_gamers(root):

    root.destroy()
    root = tk.Tk()
    #root.geometry('100x200')
    label1 = tk.Label(root, text="Wait other users:")
    label1.pack()
    users_str = ''
    users = tk.StringVar()
    users.set(users)

    label2 = tk.Label(root, text=users)
    label2.pack()

    btn = tk.Button(root, text="play", state='disabled')
    btn.pack()




def empty(root):
    root = Toplevel(root)
    root.geometry('200x100')
    name = tk.Entry(root)
    name.grid(row=0, sticky='WE')

    OPTIONS = [2, 3, 4]
    variable = IntVar(root)
    variable.set(OPTIONS[0]) # default value

    w = OptionMenu(root, variable, *OPTIONS)
    w.grid(row=1, sticky='WE')

    btn = tk.Button(root, text='Start the game', command=lambda : find_gamers(root))
    btn.grid(row=2, sticky='WE')


if __name__ == '__main__':


    root = tk.Tk()

    root.title('Cards Games')
    root.geometry('300x500')
    tmp_names = ['Blackjack', 'Fool-online']
    app_frames = [init_bj, empty]


    buttons_frame = tk.LabelFrame(  root, text="Games",
                                    height=500, width=300,
                                    labelanchor='n')

    buttons_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
    menu = MainMenu(buttons_frame, app_frames, tmp_names)

    root.mainloop()
