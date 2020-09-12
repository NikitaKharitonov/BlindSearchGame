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
        self.can_move = False  # denotes if the player can move or not

    def execute(self):
        # Initialize GUI
        if not self.ui.show():
            return

        # Initialize the socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect to the server
        while True:
            try:
                self.sock.connect((socket.gethostname(), server.PORT))
                break
            except (socket.error, OverflowError):
                pass

        # Receive information about the game state from the server (e. g. the username)
        try:
            message = model.Message(**json.loads(self.receive_all()))
        except (ConnectionAbortedError, ConnectionResetError):
            if not self.closing:
                self.ui.alert(ERROR, CONNECTION_ERROR)
            return

        self.username = message.username
        self.ui.gui.title(self.username.upper())
        self.receive_worker = threading.Thread(target=self.receive)
        self.receive_worker.start()
        self.ui.loop()

    def receive(self):
        # Receive and handle messages from  the server
        while True:
            try:
                message = model.Message(**json.loads(self.receive_all()))
            except (ConnectionAbortedError, ConnectionResetError):
                if not self.closing:
                    self.ui.alert(ERROR, CONNECTION_ERROR)
                return
            if message.can_move:
                self.can_move = True
            self.ui.show_message(message)

    def receive_all(self):
        # Receive incoming messages from the server in the buffer
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += self.sock.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def send(self):
        # Send the message to the server containing the angle of one move
        if self.can_move:
            angle = self.ui.angle.get()
            message = model.Message(angle=angle)
            try:
                self.sock.sendall(message.marshal())
            except (ConnectionAbortedError, ConnectionResetError):
                if not self.closing:
                    self.ui.alert(ERROR, CONNECTION_ERROR)
            self.can_move = False

    def exit(self):
        self.closing = True
        try:
            self.sock.sendall(model.Message(quit=True).marshal())
        except (ConnectionResetError, ConnectionAbortedError, OSError):
            print(CONNECTION_ERROR)
        finally:
            self.sock.close()


if __name__ == "__main__":
    print("heloh?")
    app = Client()
    app.execute()
