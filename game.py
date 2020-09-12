import math
from random import random
import json
import jsonschema
from jsonschema import validate

NUMBER_OF_PLAYERS = 2
MAX_INITIAL_DISTANCE = 10
MIN_INITIAL_DISTANCE = 2
MAX_ANGLE = 360

schema = {
    "type": "object",
    "properties": {
        "players": {
            "type": "array",
            "minItems": 2,
            "maxItems": 2,
            "items": [
                {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string"},
                        "x": {"type": "number"},
                        "y": {"type": "number"}
                    },
                    "required": [
                        "username",
                        "x",
                        "y"
                    ],
                    "additionalProperties": False
                }
            ]
        }
    },
    "required": [
        "players"
    ]
}


def init_distance():
    """
    Generates a random distance from the award for all players
    in the [MIN_INITIAL_DISTANCE, MAX_INITIAL_DISTANCE) interval.

    :return: the generated distance.
    """
    return MIN_INITIAL_DISTANCE + (MAX_INITIAL_DISTANCE - MIN_INITIAL_DISTANCE) * random()


def create_player_from_polar_coordinates(username, distance, angle, client):
    """
    Converts the given polar coordinates into cartesian and
    initializes a player.

    :param username: the unique name of the player.
    :param distance: the first polar coordinate.
    :param angle: the second polar coordinate.
    :param client: the client connection associated with the player.
    :return: the player with the calculated cartesian coordinates.
    """
    angle = math.radians(angle)
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    return Player(username, x, y, client)


def parse_data(data):
    """
    Parses the given dictionary to the list of Player objects.

    :param data: the dictionary containing the Player data
    :return: the list of Player objects.
    """
    players = list()
    for player_data in data['players']:
        player = Player(player_data['username'],
                        player_data['x'],
                        player_data['y'],
                        None)
        players.append(player)
    return players


def init_players():
    """
    Initializes players for the game so that the distance to the award
    is equal for all of them.

    :return: the two players as a list.
    """
    distance = init_distance()
    players = list()
    for i in range(0, 2):
        players.append(
            create_player_from_polar_coordinates(
                f"player{i}", distance, MAX_ANGLE * random(), None
            )
        )
    return players


def validate_json(data):
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


def load_game_state_from_json(json_file_path):
    """
    Loads the game state from the JSON file specified by the given path.

    :param json_file_path: the JSON file path to load from.
    :return: True when the game state has been successfully loaded,
    False otherwise.
    """
    with open(json_file_path) as json_file:
        try:
            data = json.load(json_file)
            if validate_json(data):
                return True, data
        except json.decoder.JSONDecodeError:
            pass
    return False, None


class Player:
    """
    A player of the game.
    The position of the player on the 2D game plane is described
    by the (x, y) cartesian coordinates. The award is located in the origin
    of the plane.
    """

    def __init__(self, username, x, y, client_socket):
        """
        Initializes a player.

        :param username: the unique name of the player.
        :param x: the first cartesian coordinate.
        :param y: the second cartesian coordinate.
        :param client_socket: the socket associated with the player.
        """
        self.username = username
        self.x = x
        self.y = y
        self.client_socket = client_socket

    def __str__(self):
        """
        Converts the player to a string containing the username and the coordinates.

        :return: the string representation of the player.
        """
        return f"Player username: {self.username}, x: {self.x}, y: {self.y}"

    def distance(self):
        """
        Calculates the distance to the award for the player.

        :return: the distance.
        """
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def move(self, angle):
        """
        Moves the player one unit in the given angle from the OX direction.

        :param angle: the angle.
        """
        angle = math.radians(angle)
        x = math.cos(angle)
        y = math.sin(angle)
        self.x += x
        self.y += y

    def dict(self):
        """
        Converts the player to a dictionary containing the username and the coordinates.

        :return: the dictionary representation of the player.
        """
        return {
            'username': self.username,
            'x': self.x,
            'y': self.y
        }
