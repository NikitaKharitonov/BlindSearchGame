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

    # def listen(self):
    #     self.socket.listen(1)
    #     connected_clients_count = 0
    #     while connected_clients_count != game.NUMBER_OF_PLAYERS:
    #         try:
    #             client, address = self.socket.accept()
    #         except OSError:
    #             print(CONNECTION_ABORTED)
    #             return
    #         print(CONNECTED_PATTERN.format(*address))
    #
    #         player = self.players[connected_clients_count]
    #         player.client = client
    #         client.sendall(Message(username=SERVER, message=player.username).marshal())
    #
    #         connected_clients_count += 1
    #
    #     if self.new_game:
    #         message = f"GAME BEGIN! Distance to award: {round(game.initial_distance, 3)}"
    #         self.broadcast(Message(username=SERVER, message=message))
    #     else:
    #         for player in self.players:
    #             message = f"GAME CONTINUE! Distance to award: {round(player.distance(), 3)}"
    #             player.client.sendall(Message(username=SERVER, message=message).marshal())
    #
    #     for player in self.players:
    #         print(player)
    #
    #     self.dump_game_state_to_json()
    #
    #     while True:
    #         for player in self.players:
    #             client = player.client
    #             message_from_server = Message(username=SERVER, message=MOVE_ALLOWED)
    #             client.sendall(message_from_server.marshal())
    #             try:
    #                 message = Message(**json.loads(self.receive(client)))
    #             except(ConnectionAbortedError, ConnectionResetError):
    #                 print(CONNECTION_ABORTED)
    #                 return
    #             if message.quit:
    #                 self.close_clients()
    #                 return
    #             angle = float(message.message)
    #             player.make_move(angle)
    #             message.message = f"angle: {angle % 360}, distance to award: {round(player.distance(), 3)}"
    #             self.broadcast(message)
    #             print(str(message))
    #         for player in self.players:
    #             print(player)
    #         # fixme ?
    #         if self.players[0].distance() <= 1 and self.players[1].distance() <= 1:
    #             message = "dead heat!"
    #             self.broadcast(Message(username=SERVER, message=message))
    #             print(message)
    #             self.close_clients()
    #             self.players = list()
    #             break
    #         for player in self.players:
    #             if player.distance() <= 1:
    #                 message = f"{player.username} won!"
    #                 self.broadcast(Message(username=SERVER, message=message))
    #                 print(message)
    #                 self.close_clients()
    #                 self.players = list()
    #                 return
    #         self.dump_game_state_to_json()

    def broadcast(self, message):
        for player in self.players:
            player.client_socket.sendall(message.marshal())

    def receive(self, client):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += client.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def run(self):

        # INITIALIZE

        print(RUNNING)

        success, dict = game.load_game_state_from_json(JSON_FILE_PATH)
        if success:
            self.players = game.parse_data(dict)
        else:
            self.players = game.init_players()
        self.new_game = not success

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))

        # LISTEN

        self.socket.listen(1)
        connected_clients_count = 0
        while connected_clients_count != game.NUMBER_OF_PLAYERS:
            try:
                client, address = self.socket.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))

            player = self.players[connected_clients_count]
            player.client_socket = client
            client.sendall(Message(username=SERVER, message=player.username).marshal())

            connected_clients_count += 1

        if self.new_game:
            message = f"GAME BEGIN! Distance to award: {round(self.players[0].distance(), 3)}"
            self.broadcast(Message(username=SERVER, message=message))
        else:
            for player in self.players:
                message = f"GAME CONTINUE! Distance to award: {round(player.distance(), 3)}"
                player.client_socket.sendall(Message(username=SERVER, message=message).marshal())

        for player in self.players:
            print(player)

        self.dump_game_state_to_json()

        # HANDLE

        cont = True
        while cont:

            for player in self.players:
                client = player.client_socket
                message_from_server = Message(username=SERVER, message=MOVE_ALLOWED)
                client.sendall(message_from_server.marshal())
                try:
                    message = Message(**json.loads(self.receive(client)))
                except(ConnectionAbortedError, ConnectionResetError):
                    print(CONNECTION_ABORTED)
                    return
                if message.quit:
                    cont = False
                    # self.close_clients()
                    break
                angle = float(message.message)
                player.move(angle)
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
                self.players = list()
                break

            for player in self.players:
                if player.distance() <= 1:
                    message = f"{player.username} won!"
                    self.broadcast(Message(username=SERVER, message=message))
                    print(message)
                    self.players = list()
                    cont = False
                    break

            self.dump_game_state_to_json()

        # CLOSE

        self.close_clients()
        self.dump_game_state_to_json()
        print(CLOSING)

    def close_clients(self):
        self.socket.close()
        for player in self.players:
            player.client_socket.close()
        print(CLOSING)

    def dump_game_state_to_json(self):
        data = {'players': []}
        for player in self.players:
            data['players'].append(player.dict())
        with open(JSON_FILE_PATH, 'w') as outfile:
            json.dump(data, outfile, indent=4)

    # def parse_data(self, dict):
    #     """
    #     Parses the given dictionary to the list of Player objects
    #
    #     :param dict: the dictionary containing the Player data
    #     :return: the list of Player objects
    #     """
    #     players = list()
    #     for player_data in dict['players']:
    #         player = game.recreate_player(player_data['username'],
    #                                       None,
    #                                       player_data['x'],
    #                                       player_data['y'])
    #         players.append(player)
    #     return players
    #
    # def initialize_players(self):
    #     """
    #     Initializes two players for the game so that the distance to the award
    #     is equal for both of them
    #
    #     :return: the two players as a list
    #     """
    #     return [Player(game.initial_distance, game.MAX_ANGLE * random(), None, "player0"),
    #             Player(game.initial_distance, game.MAX_ANGLE * random(), None, "player1")]
    #
    # def load_game_state_from_json(self, json_file_path):
    #     """
    #     Loads the game state from the JSON file specified by the given path
    #
    #     :param json_file_path: the JSON file path to load from
    #     :return: True when the game state has been successfully loaded,
    #     False otherwise
    #     """
    #     with open(json_file_path) as json_file:
    #         try:
    #             data = json.load(json_file)
    #             if model.validate_json(data):
    #                 return True, data
    #         except json.decoder.JSONDecodeError:
    #             pass
    #     return False, None


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
