"""Tkinter menu class."""

import gettext
import sys
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

        self.quitButton = tk.Button(self, text=_("Exit"),
                                    font=('Helvetica', 16),
                                    command=self._delete_all)
        self.quitButton.grid(row=len(apps_names), padx=10,
                             pady=20, sticky="NSEW")

        self.game_buttons = []
        for idx in range(len(apps)):

            closure = partial(self.apps[idx], self)

            btn = tk.Button(self, text=self.apps_names[idx],
                            font=('Helvetica', 16),
                            command=closure)

            btn.grid(row=idx, padx=10, pady=20, sticky='NSEW')

    def _delete_all(self):
        self.destroy()
        for children in self.master.master.winfo_children():
            children.destroy()

        self.master.master.destroy()


def init_blackjack(root):
    """Launch Blackjack."""
    # root.master.withdraw()
    root = tk.Toplevel(root)
    root.title(_("Blackjack"))
    root.geometry('890x670')

    H1 = Hand(root, 0, allow_movement=False)
    H1.show([None, None, None, None, None, None])

    H2 = Hand(root, 2)
    H2.show([None, None, None, None, None, None])

    Blackjack(root, row=1, hands=[H1, H2], player_hand=1)


def find_gamers(root):
    """Launch Fool online."""
    Main(root)


def init_queen(root):
    """Launch Queen."""
    root = tk.Toplevel(root)
    root.title(_("Queen"))
    root.geometry('890x900')

    H1 = Queen_Hand(root, row=0, show_cards=False, allow_movement=False)

    H2 = Queen_Hand(root, row=1, show_cards=False, allow_movement=False)

    H3 = Queen_Hand(root, row=3, show_cards=True, allow_movement=True)

    Queen(root, row=2, hands=[H1, H2, H3], player_hand=2)


if __name__ == '__main__':

    if len(sys.argv) > 1:
        translation = sys.argv[1]
    else:
        translation = 'eng'

    language = gettext.translation(
        domain='CardGames',
        localedir='./localization/',
        languages=[translation]
    )
    language.install()

    root = tk.Tk()
    root.title(_("Cards Games"))
    root.geometry('300x500')

    tmp_names = [_("Blackjack"), _("Fool-online"), _("Queen")]
    app_frames = [init_blackjack, find_gamers, init_queen]

    buttons_frame = tk.LabelFrame(root, text=_("Games"),
                                  height=500, width=300,
                                  labelanchor='n')

    buttons_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
    menu = MainMenu(buttons_frame, app_frames, tmp_names)

    root.mainloop()
