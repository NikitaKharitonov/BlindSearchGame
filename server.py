import json
import socket
import game
from model import Message
import model

BUFFER_SIZE = 2 ** 10
PORT = 1234
CLOSING = "Application closing..."
CONNECTION_ABORTED = "Connection aborted"
CONNECTED_PATTERN = "Client connected: {}:{}"
ERROR_OCCURRED = "Error Occurred"
RUNNING = "Server is running..."
JSON_FILE_PATH = "data.json"


class Server(object):

    def __init__(self):
        self.players = list()
        self.port = PORT
        self.socket = None

    def broadcast(self, message):
        for player in self.players:
            player.client_socket.sendall(message.marshal())

    def receive(self, client_socket):
        buffer = ""
        while not buffer.endswith(model.END_CHARACTER):
            buffer += client_socket.recv(BUFFER_SIZE).decode(model.TARGET_ENCODING)
        return buffer[:-1]

    def send(self, client_socket, message):
        client_socket.sendall(message.marshal())

    def close_client_sockets(self):
        self.socket.close()
        for player in self.players:
            player.client_socket.close()

    def run(self):

        # INITIALIZE

        print(RUNNING)

        # Initialize the game state
        success, data = game.load_game_state_from_json(JSON_FILE_PATH)
        if success:
            self.players = game.parse_data(data)
        else:
            self.players = game.init_players()
        new_game = not success

        # Initialize the socket
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(("", self.port))

        # LISTEN

        self.socket.listen(1)
        connected_clients_count = 0

        # Get the client sockets in the quantity equal to the game.NUMBER_OF_PLAYERS
        # and assign them to their Player instances.
        while connected_clients_count != game.NUMBER_OF_PLAYERS:
            try:
                client_socket, address = self.socket.accept()
            except OSError:
                print(CONNECTION_ABORTED)
                return
            print(CONNECTED_PATTERN.format(*address))
            player = self.players[connected_clients_count]
            player.client_socket = client_socket
            self.send(client_socket, Message(username=player.username))
            connected_clients_count += 1

        if new_game:
            # message = f"GAME BEGIN! Distance to award: {round(self.players[0].distance(), 3)}"
            message = Message(game_begin=True, distance=round(self.players[0].distance(), 3))
            self.broadcast(message)
            print(message)
        else:
            for player in self.players:
                # message = f"GAME CONTINUE! Distance to award: {round(player.distance(), 3)}"
                message = Message(game_continue=True, distance=round(player.distance(), 3))
                self.send(player.client_socket, message)
                print(message)

        for player in self.players:
            print(player)

        game.dump_game_state_to_json(self.players, JSON_FILE_PATH)

        # HANDLE

        cont = True
        while cont:
            # Receive and handle the moves of the players in a row
            for player in self.players:
                client_socket = player.client_socket
                message_from_server = Message(can_move=True)
                self.send(client_socket, message_from_server)
                try:
                    message = Message(**json.loads(self.receive(client_socket)))
                except(ConnectionAbortedError, ConnectionResetError):
                    print(CONNECTION_ABORTED)
                    return
                if message.quit:
                    cont = False
                    break
                player.move(message.angle)
                message.username = player.username.upper()
                message.distance = player.distance()
                self.broadcast(message)
                print(message)

            for player in self.players:
                print(player)

            # Check how many players won
            how_many_players_won = list()
            for player in self.players:
                if player.won():
                    how_many_players_won.append(player)

            # Check if one player won and end the game if yes
            if len(how_many_players_won) == 1:
                message = Message(win=True, username=how_many_players_won[0].username)
                self.broadcast(message)
                print(message)
                self.players = list()
                break

            # Check if many players won and end the game if yes
            if len(how_many_players_won) > 1:
                message = Message(nichya=True)
                self.broadcast(message)
                print(message)
                self.players = list()
                break

            game.dump_game_state_to_json(self.players, JSON_FILE_PATH)

        # CLOSE

        self.close_client_sockets()
        game.dump_game_state_to_json(self.players, JSON_FILE_PATH)
        print(CLOSING)


if __name__ == "__main__":
    try:
        Server().run()
    except RuntimeError as error:
        print(ERROR_OCCURRED)
        print(str(error))
