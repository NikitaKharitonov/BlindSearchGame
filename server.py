import json
import socket
from random import random
from game import Player
import game
from model import Message
import model

BUFFER_SIZE = 2 ** 10

CLOSING = "Application closing..."
CONNECTION_ABORTED = "Connection aborted"
CONNECTED_PATTERN = "Client connected: {}:{}"
ERROR_ARGUMENTS = "Provide port number as the first command line argument"
ERROR_OCCURRED = "Error Occurred"
EXIT = "exit"
JOIN_PATTERN = "{username} has joined"
RUNNING = "Server is running..."
SERVER = "SERVER"
SHUTDOWN_MESSAGE = "shutdown"
TYPE_EXIT = "Type 'exit' to exit>"
MOVE_ALLOWED = "your move"


class Server(object):

    def __init__(self):
        self.players = list()
        self.port = 1234
        self.socket = None

    def listen(self):
        self.socket.listen(1)
        while len(self.players) != game.NUMBER_OF_PLAYERS:
            try:
                client, address = self.socket.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))
            try:
                message = Message(**json.loads(self.receive(client)))
            except(ConnectionAbortedError, ConnectionResetError):
                print(CONNECTION_ABORTED)
                return
            username = message.username
            player = Player(game.initial_distance, game.MAX_ANGLE * random(), client, username)
            self.players.append(player)
        self.broadcast(Message(username=SERVER, message=f"GAME BEGIN! Distance to award: {round(game.initial_distance, 3)}"))
        self.handle()

    def handle(self):
        while True:
            for player in self.players:
                client = player.client
                message_from_server = Message(username=SERVER, message=MOVE_ALLOWED)
                client.sendall(message_from_server.marshal())
                try:
                    message = Message(**json.loads(self.receive(client)))
                except(ConnectionAbortedError, ConnectionResetError):
                    print(CONNECTION_ABORTED)
                    return
                if message.quit:
                    client.close()
                    self.players.remove(player)
                    self.players[0].sendall(Message(username={player.name}, message="quits"))
                    self.players[0].client.close()
                    self.players.remove(self.players[0])
                    return
                angle = float(message.message)
                player.make_move(angle)
                message.message = f"angle: {angle % 360}, distance to award: {round(player.distance(), 3)}"
                self.broadcast(message)
                print(str(message))
            for player in self.players:
                print(player)
            # fixme ?
            if self.players[0].distance() <= 1 and self.players[1].distance() <= 1:
                message = "dead heat!"
                self.broadcast(Message(username=SERVER, message=message))
                print(message)
                break
            for player in self.players:
                if player.distance() <= 1:
                    message = f"{player.name} won!"
                    self.broadcast(Message(username=SERVER, message=message))
                    print(message)
                    return

    def broadcast(self, message):
        for player in self.players:
            player.client.sendall(message.marshal())

    def receive(self, client):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += client.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def run(self):
        print(RUNNING)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.listen()

    def exit(self):
        self.socket.close()
        for player in self.players:
            player.client.close()
        print(CLOSING)


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
