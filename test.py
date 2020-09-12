import json
from game import Player
from jsonschema import validate
from model import Message

message = Message(can_move=True)
print(message)