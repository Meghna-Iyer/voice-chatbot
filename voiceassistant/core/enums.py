from enum import Enum

class MessageType(Enum):
    TEXT = 1
    AUDIO = 2

class MessageUserType(Enum):
    USER = 1
    BOT = 2