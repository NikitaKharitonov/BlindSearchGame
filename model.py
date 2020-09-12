import json
import jsonschema
from jsonschema import validate

END_CHARACTER = "\0"
MESSAGE_PATTERN = "{username}>{message}"
TARGET_ENCODING = "utf-8"

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


# todo simplify
def validate_json(data):
    try:
        validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError as err:
        return False
    return True


class Message(object):
    def __init__(self, **kwargs):
        self.username = None
        self.message = None
        self.quit = False
        self.__dict__.update(kwargs)

    def __str__(self):
        return MESSAGE_PATTERN.format(**self.__dict__)

    def marshal(self):
        return (json.dumps(self.__dict__) + END_CHARACTER).encode(TARGET_ENCODING)
