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
        # self.log = ''
        self.new_game = True
        self.data = {}

    def listen(self):
        self.socket.listen(1)
        while len(self.players) != game.NUMBER_OF_PLAYERS:
            try:
                client, address = self.socket.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))
            # try:
            #     message = Message(**json.loads(self.receive(client)))
            # except(ConnectionAbortedError, ConnectionResetError):
            #     print(CONNECTION_ABORTED)
            #     return
            if self.new_game:
                username = f"player{len(self.players)}"
                client.sendall(Message(username=SERVER, message=username).marshal())
                player = Player(game.initial_distance, game.MAX_ANGLE * random(), client, username)
                self.players.append(player)
            else:
                player_data = self.data['players'][len(self.players)]
                player = game.recreate_player(player_data['username'],
                                              client,
                                              player_data['x'],
                                              player_data['y'])
                self.players.append(player)
                client.sendall(Message(username=SERVER, message=player.username).marshal())

        if self.new_game:
            message = f"GAME BEGIN! Distance to award: {round(game.initial_distance, 3)}"
            self.broadcast(Message(username=SERVER, message=message))
            # self.log += message + '\n'
        else:
            for player in self.players:
                message = f"GAME CONTINUE! Distance to award: {round(player.distance(), 3)}"
                player.client.sendall(Message(username=SERVER, message=message).marshal())
                # self.log += message + '\n'

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
                    self.exit()
                    # client.close()
                    # self.players.remove(player)
                    # self.players[0].sendall(Message(username={player.username}, message="quits"))
                    # self.players[0].client.close()
                    # self.players.remove(self.players[0])
                    return
                angle = float(message.message)
                player.make_move(angle)
                message.message = f"angle: {angle % 360}, distance to award: {round(player.distance(), 3)}"
                self.broadcast(message)
                # self.log += message.message + '\n'
                print(str(message))
            for player in self.players:
                print(player)
            # fixme ?
            if self.players[0].distance() <= 1 and self.players[1].distance() <= 1:
                message = "dead heat!"
                self.broadcast(Message(username=SERVER, message=message))
                # self.log += message + '\n'
                print(message)
                self.exit()
                self.players.clear()
                break
            for player in self.players:
                if player.distance() <= 1:
                    message = f"{player.username} won!"
                    self.broadcast(Message(username=SERVER, message=message))
                    # self.log += message + '\n'
                    print(message)
                    self.exit()
                    self.players.clear()
                    return
            self.save()

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

        # load data from json file
        with open('data.json') as json_file:
            data = json.load(json_file)
        if model.validate_json(data):
            self.new_game = False
            self.data = data

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.listen()

        # self.players.clear()

        self.save()
        print(CLOSING)

    def exit(self):
        self.socket.close()
        for player in self.players:
            player.client.close()
        print(CLOSING)

    def save(self):
        # while len(self.players) == 2:
        data = {'players': []}
        for player in self.players:
            data['players'].append(player.json())
        with open('data.json', 'w') as outfile:
            json.dump(data, outfile, indent=4)
        # log = {'text': self.log}
        # with open('log.json', 'w') as outfile:
        #     json.dump(log, outfile, indent=4)
            # time.sleep(5)


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
