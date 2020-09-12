import json
from game import Player
from jsonschema import validate


json_schema = {
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
                    }
                }
            ]
        }
    }
}

player = Player('nikita', 1, 2, None)
print(dict(player))