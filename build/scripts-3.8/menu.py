"""Tkinter menu class."""

import tkinter as tk


from blackjack import Blackjack
from FoolOnline import Main
from queen import Queen, Queen_Hand
from cards import Hand

from functools import partial


class MainMenu(tk.Frame):
    """Menu that launch card games."""

    def __init__(self, master, apps, apps_names):
        """Create tkinter GUI."""
        assert len(apps) == len(apps_names)

        self.apps = apps
        self.apps_names = apps_names

        tk.Frame.__init__(self, master)

        self.grid(sticky=tk.N + tk.E + tk.S + tk.W)
        top = self.winfo_toplevel()
        top.rowconfigure(0, weight=1)
        self.rowconfigure(tuple((i for i in range(len(apps_names)))), weight=1)

        self.quitButton = tk.Button(self, text='Exit',
                                    font=('Helvetica', 16),
                                    command=self.delete_all)
        self.quitButton.grid(row=len(apps_names), padx=10,
                             pady=20, sticky="NSEW")

        self.game_buttons = []
        for idx in range(len(apps)):

            closure = partial(self.apps[idx], self)

            btn = tk.Button(self, text=self.apps_names[idx],
                            font=('Helvetica', 16),
                            command=closure)

            btn.grid(row=idx, padx=10, pady=20, sticky='NSEW')

    def delete_all(self):
        for children in self.master.winfo_children():
            children.destroy()

        self.master.destroy()
        self.master.quit()


    '''

    def change_frame(self, fr):

        fr.reset()
        fr.tkraise()
    '''

def init_bj(root):
    """Launch Blackjeck."""
    # root.master.withdraw()
    root = tk.Toplevel(root)
    root.geometry('1000x900')

    H1 = Hand(root, 0)
    H1.show([None, None, None, None, None, None])

    H2 = Hand(root, 2)
    H2.show([None, None, None, None, None, None])

    Blackjack(root, row=1, hands=[H1, H2], player_hand=1)


def find_gamers(root):
    """Launch Fool online."""
    Main(root)


def queen(root):
    """Launch Queen."""
    root = tk.Toplevel(root)
    root.geometry('870x900')

    H1 = Queen_Hand(root, row=0, show_cards=False, allow_movement=False)

    H2 = Queen_Hand(root, row=1, show_cards=False, allow_movement=False)

    H3 = Queen_Hand(root, row=3, show_cards=True, allow_movement=True)

    Queen(root, row=2, hands=[H1, H2, H3], player_hand=2)


if __name__ == '__main__':

    root = tk.Tk()

    root.title('Cards Games')
    root.geometry('300x500')
    tmp_names = ['Blackjack', 'Fool-online', 'Queen']
    app_frames = [init_bj, find_gamers, Queen]

    buttons_frame = tk.LabelFrame(root, text="Games",
                                  height=500, width=300,
                                  labelanchor='n')

    buttons_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    menu = MainMenu(buttons_frame, app_frames, tmp_names)

    root.mainloop()
