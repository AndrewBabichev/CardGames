import tkinter as tk
import sys
import websocket
import json

from functools import partial
from threading import Thread
from queue import Queue

from fool_cards import OnlineReferee, FoolDeck, Player, Table, ScoreTable
RESOURSES_DIR = 'resourses/cards'
EMPTY_CARD = 'empty.png'
BACK_CARD = 'back.png'
STATUS = 'Attacked'


class ConnectionFinder():

    def __init__(self, main, settings, game_server, chat_server):

        self.root = main
        self.main = tk.Toplevel(main)
        self.main.title("Game Settings")
        self.settings = settings
        self.game_server = game_server
        self.chat_server = chat_server

        self.error = False
        name_lab = tk.Label(self.main, text='Your name:')
        name_lab.grid(row=0, column=0)

        self.name = tk.StringVar()
        name_entry = tk.Entry(self.main, textvariable=self.name)
        name_entry.grid(row=0, column=1, columnspan=2)

        self.num_players = 2
        next_btn = tk.Button(self.main,
                             text='Next',
                             command=partial(self.findConnection,
                                             self.num_players,
                                             self.name))

        next_btn.grid(row=1, column=1)
        tk.Button(self.main, text="Quit",
                  command=lambda: self.quit()).grid(row=1, column=0)

    def __get_errro_msg(self, msg):
        root = tk.Toplevel(self.main)
        root.title("Error")

        lab = tk.Label(root, text=msg)
        lab.pack()

        btn = tk.Button(root, text='Ok',
                        command=lambda root=root: root.destroy())
        btn.pack()

    def findConnection(self, num_players, player_name):
        params = {'num_players': num_players,
                  'player_name': player_name.get()}

        def game_connect():
            try:
                ws = websocket.create_connection(self.game_server)
                ws.send(json.dumps({
                    'type': 'look_up',
                    'message': params}
                ))
                return ws

            except Exception:
                print("error")
                self.error = True
                self.__get_errro_msg(
                    "Connection error has occured!\nTry connect later..."
                )

                self.quit()

        def chat_connect():

            try:
                ws_chat = websocket.create_connection(self.chat_server)
            except Exception:
                print("error")
                self.error = True
                self.__get_errro_msg(
                    "Connection error has occured!\nTry connect later..."
                )

                self.quit()

            return ws_chat

        ws_game = game_connect()
        if self.error:
            self.quit()
        else:
            ws_chat = chat_connect()
        self.settings['game_socket'] = ws_game
        self.settings['chat_socket'] = ws_chat
        self.settings['name'] = player_name.get()
        self.open_app()

    def open_app(self):
        App(self.main, self.settings)


class ChatWindow(tk.Toplevel):

    def __init__(self, main, ws, name, queue, listen_thread=None):

        super().__init__(main)
        self.title("Game messenger")

        self.ws = ws
        self.name = name
        self.queue = queue
        self.listen_thread = listen_thread
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)

        self.text = tk.Text(self, height=20, width=40)
        self.text.grid(row=0, columnspan=2)

        self.textVar = tk.StringVar()
        self.entry = tk.Entry(self, textvariable=self.textVar)
        self.entry.grid(row=1, column=0)

        self.send_btn = tk.Button(self, text='Send', command=self.send)
        self.send_btn.grid(row=1, column=1)

        self.updateGUI()

    def __on_closing(self):
        self.ws.close()

    def updateGUI(self):

        if self.listen_thread is None or not self.listen_thread.is_alive():
            return

        while not self.queue.empty():
            item = self.queue.get()
            _, msg = item['type'], item['message']
            self.text.insert(tk.END, '[{}] {} : {}\n'.format(msg['time'],
                                                             msg['sender'],
                                                             msg['payload'])
                             )

        self.after(500, self.updateGUI)

    def send(self):

        def send_message():
            self.ws.send(json.dumps({
                'type': 'chat_message',
                'message': {
                    'sender': self.name,
                    'payload': self.entry.get()
                }
            }))

        send_message()
        self.entry.delete(0, 'end')


class FoolGame(tk.Toplevel):

    def __init__(
            self,
            main,
            name,
            ws_game,
            ws_chat,
            queue,
            listen_thread=None):

        super().__init__(main)

        self.main = main
        self.title("Fool-online")
        self.geometry("1400x900")
        self.protocol("WM_DELETE_WINDOW", self.__on_closing)
        self.name = name
        self.ws_game = ws_game
        self.ws_chat = ws_chat
        self.queue = queue
        self.listen_thread = listen_thread

        self.info_pool = []
        self.stage = 0

        # -----------------------------------------------------------------------
        self.info_frame = tk.Frame(self)
        self.info_frame.place(relx=0.5, rely=0.05)
        self.info_s = tk.StringVar()
        self.info = tk.Label(self.info_frame, text="Info:")
        self.info_var = tk.Label(self.info_frame, textvariable=self.info_s)
        self.info.grid(row=0, column=0)
        self.info_var.grid(row=0, column=1)
        # -----------------------------------------------------------------------

        self.referee = OnlineReferee(ws_game, ws_chat)
        self.referee.info = self.info_s

        self.deck = FoolDeck(self, 'resourses/cards', 1, self.referee)
        self.referee.deck = self.deck

        self.player = Player(self, 2, self.name, self.referee)
        self.referee.player = self.player

        self.table = Table(self, 0.53, 0.6, 4, self.referee)
        self.referee.table = self.table

        self.score_table = ScoreTable(self, 0.75, 0.1)
        self.referee.score_table = self.score_table

        self.updateGUI()

    def updateGUI(self):

        if self.listen_thread is None or not self.listen_thread.is_alive():
            return

        while not self.queue.empty():

            msg = self.queue.get()
            self.referee.handle_message(msg)

        self.after(300, self.updateGUI)

    def __on_closing(self):
        self.ws_game.close()
        self.ws_chat.close()
        for child in self.main.winfo_children():
            child.destroy()

        self.main.quit()


class App():

    def __init__(self, main, settings):

        self.chat_queue = Queue()
        self.game_queue = Queue()

        self.game_socket = settings['game_socket']
        self.chat_socket = settings['chat_socket']
        name = settings['name']

        self.game_thread = Thread(
            target=self.__listen_socket,
            args=(self.game_socket, self.game_queue))

        self.chat_thread = Thread(
            target=self.__listen_socket,
            args=(self.chat_socket, self.chat_queue))

        self.game_thread.start()
        self.chat_thread.start()

        FoolGame(
            main,
            name,
            self.game_socket,
            self.chat_socket,
            self.game_queue,
            self.game_thread)
        ChatWindow(
            main,
            self.chat_socket,
            name,
            self.chat_queue,
            self.chat_thread)

    def __listen_socket(self, socket, q):

        while True:

            try:
                msg = socket.recv()
            except Exception:
                break

            if len(msg):
                msg = json.loads(msg)
                q.put(msg)


class Main():
    def __init__(self, main):
        # super().__init__()

        self.main = main
        self.settings = {}
        self.server_addr = "polar-depths-25815.herokuapp.com"
        if len(sys.argv) > 1:
            self.server_addr = sys.argv[1]

        self.server_game_addr = "ws://{}/game".format(self.server_addr)
        self.server_chat_addr = "ws://{}/chat".format(self.server_addr)

        self.app = ConnectionFinder(main, self.settings,
                                    self.server_game_addr,
                                    self.server_chat_addr
                                    )


'''
if __name__ == '__main__':

    m = Main()
    m.mainloop()
'''
