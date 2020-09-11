import json
import socket
import threading
import model
import view
import server

BUFFER_SIZE = 2 ** 10

CONNECTION_ERROR = "Could not connect to server"
ERROR = "Error"


class Client(object):
    instance = None

    def __init__(self):
        self.closing = False
        self.receive_worker = None
        self.sock = None
        self.username = None
        self.ui = view.BlindSearchGameUI(self)
        Client.instance = self
        self.move = False

    def execute(self):
        if not self.ui.show():
            return
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.sock.connect((socket.gethostname(), 1234))
        except (socket.error, OverflowError):
            self.ui.alert(ERROR, CONNECTION_ERROR)
            return

        try:
            username = model.Message(**json.loads(self.receive_all()))
        except (ConnectionAbortedError, ConnectionResetError):
            if not self.closing:
                self.ui.alert(ERROR, CONNECTION_ERROR)
            return
        self.username = username.message
        self.ui.gui.title(self.username.upper())
        # message = model.Message(username=self.username, message="", quit=False)
        # try:
        #     self.sock.sendall(message.marshal())
        # except (ConnectionAbortedError, ConnectionResetError):
        #     if not self.closing:
        #         self.ui.alert(ERROR, CONNECTION_ERROR)
        self.receive_worker = threading.Thread(target=self.receive)
        self.receive_worker.start()
        self.ui.loop()

    def receive(self):
        while True:
            try:
                message = model.Message(**json.loads(self.receive_all()))
            except (ConnectionAbortedError, ConnectionResetError):
                if not self.closing:
                    self.ui.alert(ERROR, CONNECTION_ERROR)
                return
            if message.message == server.MOVE_ALLOWED:
                self.move = True
            self.ui.show_message(message)

    def receive_all(self):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += self.sock.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]


    def send(self, event=None):
        if self.move:
            message = self.ui.message.get()
            # self.ui.message.set("")
            message = model.Message(username=self.username, message=message, quit=False)
            try:
                self.sock.sendall(message.marshal())
            except (ConnectionAbortedError, ConnectionResetError):
                if not self.closing:
                    self.ui.alert(ERROR, CONNECTION_ERROR)
            self.move = False

    def exit(self):
        self.closing = True
        try:
            self.sock.sendall(model.Message(username=self.username, message="", quit=True).marshal())
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            print(CONNECTION_ERROR)
        finally:
            self.sock.close()


if __name__ == "__main__":
    print("Heloh?".lower())
    app = Client()
    app.execute()
