from enum import Enum

directions_vectors = {
    "N": (1, 0),
    "E": (0, 1),
    "S": (-1, 0),
    "W": (0, -1)
}

turn_actions = {
    ('N', 'E'): ['TURN_RIGHT'],
    ('N', 'W'): ['TURN_LEFT'],
    ('N', 'S'): ['TURN_RIGHT', 'TURN_RIGHT'],
    ('S', 'E'): ['TURN_LEFT'],
    ('S', 'W'): ['TURN_RIGHT'],
    ('S', 'N'): ['TURN_RIGHT', 'TURN_RIGHT'],
    ('E', 'N'): ['TURN_LEFT'],
    ('E', 'S'): ['TURN_RIGHT'],
    ('E', 'W'): ['TURN_RIGHT', 'TURN_RIGHT'],
    ('W', 'N'): ['TURN_RIGHT'],
    ('W', 'S'): ['TURN_LEFT'],
    ('W', 'E'): ['TURN_RIGHT', 'TURN_RIGHT']
}

class State(Enum):
    POSITION = 0
    DIRECTION = 1
    EVENT = 2
    POINT = 3
    HP = 4
    HEAL_POTIONS = 5