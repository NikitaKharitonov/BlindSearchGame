import json

END_CHARACTER = "\0"
MOVE_PATTERN = "{username}> angle: {angle}, distance to award: {distance}"
GAME_BEGIN = "GAME BEGIN! Distance to award: {distance}"
GAME_CONTINUE = "GAME CONTINUE! Distance to award: {distance}"
YOUR_MOVE = "You move"
NICHYA = "Nichya!"
WIN_PATTERN = "{username} won!"
TARGET_ENCODING = "utf-8"


class Message(object):
    def __init__(self, **kwargs):
        self.username = None
        self.angle = 0
        self.distance = 0
        self.game_begin = False
        self.game_continue = False
        self.can_move = False
        self.quit = False
        self.nichya = False
        self.win = False
        self.__dict__.update(kwargs)

    def __str__(self):
        if self.game_begin:
            return GAME_BEGIN.format(**self.__dict__)
        if self.game_continue:
            return GAME_CONTINUE.format(**self.__dict__)
        if self.can_move:
            return YOUR_MOVE
        if self.nichya:
            return NICHYA
        if self.win:
            return WIN_PATTERN.format(**self.__dict__)
        return MOVE_PATTERN.format(**self.__dict__)

    def marshal(self):
        return (json.dumps(self.__dict__) + END_CHARACTER).encode(TARGET_ENCODING)
