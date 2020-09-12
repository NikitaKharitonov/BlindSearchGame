import json
import socket
from random import random
from game import Player
import game
from model import Message
import model

BUFFER_SIZE = 2 ** 10
PORT = 1234

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
JSON_FILE_PATH = "data.json"


class Server(object):

    def __init__(self):
        self.players = list()
        self.port = PORT
        self.socket = None
        self.new_game = True
        self.game_state = {}

    def listen(self):
        self.socket.listen(1)
        connected_clients_count = 0
        while connected_clients_count != game.NUMBER_OF_PLAYERS:
            try:
                client, address = self.socket.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))

            if self.new_game:
                player = self.players[connected_clients_count]
                player.client = client
                # username = f"player{len(self.players)}"
                client.sendall(Message(username=SERVER, message=player.username).marshal())
                # player = Player(game.initial_distance, game.MAX_ANGLE * random(), client, username)
                # self.players.append(player)
            else:
                # player_data = self.game_state['players'][len(self.players)]
                # player = game.recreate_player(player_data['username'],
                #                               client,
                #                               player_data['x'],
                #                               player_data['y'])
                player = self.players[connected_clients_count]
                player.client = client
                # self.players.append(player)
                client.sendall(Message(username=SERVER, message=player.username).marshal())
            connected_clients_count += 1

        if self.new_game:
            message = f"GAME BEGIN! Distance to award: {round(game.initial_distance, 3)}"
            self.broadcast(Message(username=SERVER, message=message))
        else:
            for player in self.players:
                message = f"GAME CONTINUE! Distance to award: {round(player.distance(), 3)}"
                player.client.sendall(Message(username=SERVER, message=message).marshal())
        for player in self.players:
            print(player)
        self.dump_game_state_to_json()
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
                    self.close_clients()
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
                self.close_clients()
                self.players = list()
                break
            for player in self.players:
                if player.distance() <= 1:
                    message = f"{player.username} won!"
                    self.broadcast(Message(username=SERVER, message=message))
                    print(message)
                    self.close_clients()
                    self.players = list()
                    return
            self.dump_game_state_to_json()

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

        success, data = self.load_game_state_from_json()
        if success:
            self.parse_data(data)
        else:
            self.initialize_players()
        self.new_game = not success


        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))
        self.listen()

        self.dump_game_state_to_json()
        print(CLOSING)

    def close_clients(self):
        self.socket.close()
        for player in self.players:
            player.client.close()
        print(CLOSING)

    def dump_game_state_to_json(self):
        data = {'players': []}
        for player in self.players:
            data['players'].append(player.json())
        with open(JSON_FILE_PATH, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    def parse_data(self, data):
        for player_data in data['players']:
            player = game.recreate_player(player_data['username'],
                                          None,
                                          player_data['x'],
                                          player_data['y'])
            self.players.append(player)

    def initialize_players(self):
        self.players = (Player(game.initial_distance, game.MAX_ANGLE * random(), None, "player0"),
                        Player(game.initial_distance, game.MAX_ANGLE * random(), None, "player1"))

    def load_game_state_from_json(self):
        """
        Loads the game state from the JSON file specified by JSON_FILE_PATH
        :return: True when the game state has been successfully loaded,
        False otherwise
        """
        with open(JSON_FILE_PATH) as json_file:
            try:
                data = json.load(json_file)
                if model.validate_json(data):
                    # self.new_game = False
                    self.game_state = data
                    # for player_data in data['players']:
                    #     player = game.recreate_player(player_data['username'],
                    #                                   None,
                    #                                   player_data['x'],
                    #                                   player_data['y'])
                    #     self.players.append(player)
                    return True, data
            except json.decoder.JSONDecodeError:
                pass
        return False, None


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
