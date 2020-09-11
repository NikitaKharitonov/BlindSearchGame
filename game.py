import math
from random import random

NUMBER_OF_PLAYERS = 2
MAX_INITIAL_DISTANCE = 10
MIN_INITIAL_DISTANCE = 2
MAX_ANGLE = 360

initial_distance = MIN_INITIAL_DISTANCE + (MAX_INITIAL_DISTANCE - MIN_INITIAL_DISTANCE) * random()


def recreate_player(username, client, x, y):
    distance = math.sqrt(x ** 2 + y ** 2)
    angle = math.atan2(y, x)
    return Player(distance, angle, client, username)


class Player:

    def __init__(self, distance, angle, client, username=""):
        angle = math.radians(angle)
        self.x = distance * math.cos(angle)
        self.y = distance * math.sin(angle)
        self.client = client
        self.username = username

    def distance(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def make_move(self, angle):
        angle = math.radians(angle)
        x = math.cos(angle)
        y = math.sin(angle)
        self.x += x
        self.y += y

    def __str__(self):
        return f"Player name: {self.username}, x: {self.x}, y: {self.y}"

    def json(self):
        return {
            'username': self.username,
            'x': self.x,
            'y': self.y
        }
