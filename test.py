import json
from game import Player
from jsonschema import validate
from model import Message

message = Message(username='ali', message='merhaba')
print(message.__dict__)
print(json.load(fp='data.json'))