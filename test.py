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

with open('data.json') as json_file:
    data = json.load(json_file)

validate(instance=data, schema=json_schema)

print(data['players'])