import math
from random import random

NUMBER_OF_PLAYERS = 2
MAX_INITIAL_DISTANCE = 10
MIN_INITIAL_DISTANCE = 2
MAX_ANGLE = 360

initial_distance = MIN_INITIAL_DISTANCE + (MAX_INITIAL_DISTANCE - MIN_INITIAL_DISTANCE) * random()


class Player:

    def __init__(self, distance, angle, client, name=""):
        angle = math.radians(angle)
        self.x = distance * math.cos(angle)
        self.y = distance * math.sin(angle)
        self.client = client
        self.name = name

    def distance(self):
        return math.sqrt(self.x ** 2 + self.y ** 2)

    def make_move(self, angle):
        angle = math.radians(angle)
        x = math.cos(angle)
        y = math.sin(angle)
        self.x += x
        self.y += y

    def __str__(self):
        return f"Player name: {self.name}, x: {self.x}, y: {self.y}"

