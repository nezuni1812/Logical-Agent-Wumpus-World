from enum import Enum

directions = {
    "N": (1, 0),
    "E": (0, 1),
    "S": (-1, 0),
    "W": (0, -1)
}

class State(Enum):
    POSITION = 0
    DIRECTION = 1
    EVENT = 2
    POINT = 3
    HP = 4
    HEAL_POTIONS = 5