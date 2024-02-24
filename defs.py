from enum import Enum
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass


class Color(Enum):
    RED = "R"
    GREEN = "G"
    BLACK = "B"

class Face(Enum):
    ONE = "1"
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    DRAGON = "D"
    ROSE = "R"
    TAKEN = "T"
    EMPTY = "E"

NUMERIC = [Face.ONE, Face.TWO, Face.THREE, Face.FOUR, Face.FIVE, Face.SIX, Face.SEVEN, Face.EIGHT, Face.NINE]

banner = """
░       ░░░       ░░░░      ░░░░      ░░░░      ░░░   ░░░  ░
▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒▒▒▒▒  ▒▒▒▒  ▒▒    ▒▒  ▒
▓  ▓▓▓▓  ▓▓       ▓▓▓  ▓▓▓▓  ▓▓  ▓▓▓   ▓▓  ▓▓▓▓  ▓▓  ▓  ▓  ▓
█  ████  ██  ███  ███        ██  ████  ██  ████  ██  ██    █
█       ███  ████  ██  ████  ███      ████      ███  ███   █
                                                            
░       ░░░  ░░░░  ░░   ░░░  ░░░      ░░░  ░░░░  ░          
▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒▒    ▒▒  ▒▒  ▒▒▒▒  ▒▒  ▒▒▒▒  ▒          
▓       ▓▓▓  ▓▓▓▓  ▓▓  ▓  ▓  ▓▓  ▓▓▓▓▓▓▓▓        ▓          
█  ████████  ████  ██  ██    ██  ████  ██  ████  █          
█  █████████      ███  ███   ███      ███  ████  █          
                                                            
"""

@dataclass
class Card:
    color: Color
    face: Face

    def __str__(self):
        return self.face.value + self.color.value
    
    @classmethod
    def from_str(cls, s: str):
        return cls(Color(s[1]), Face(s[0]))

@dataclass
class Board:
    special: List[Card]
    rows: List[List[Card]]

    @classmethod
    def new(cls):
        return cls(
            [Card.from_str("EB"), Card.from_str("EB"), Card.from_str("EB")],
            [[], [], [], [], [], [], [], []],
        )

    def get_hash(self) -> str:
        h = ""
        strrows = []
        for r in self.rows:
            if len(r) == 0:
                continue
            strrows.append("".join([str(x) for x in r]))
            strrows.sort()
        h += "|".join(strrows)
        return h

    def allcards(self) -> List[Card]:
        return self.special + [c for r in self.rows for c in r]

#First print all specdial cards then skip two rows and print wins
#Then print all rows but vertically
    def show(self):
        mins = {Color.RED: 10, Color.GREEN: 10, Color.BLACK: 10}
        maxlen = max([len(r) for r in self.rows])
        for c in self.allcards():
            if c.face in NUMERIC:
                mins[c.color] = min(mins[c.color], int(c.face.value))
        for i in range(3):
            print(self.special[i] or "__", end=" ")
        print("  ", end=" ")
        for c in mins:
            print(c.value, mins[c], end=" ")
        print()

        for j in range(maxlen):
            for i in range(8):
                try:
                    print(self.rows[i][j], end=" ")
                except IndexError:
                    print("__", end=" ")
            print()

@dataclass
class BoardSlot:
    look: Tuple[int, int, int, int]
    click: Tuple[int, int]

@dataclass
class Slots:
    special: List[BoardSlot]
    rows: List[BoardSlot]
    dragons: List[BoardSlot]

slots = Slots(
    special=[
        BoardSlot((410, 131, 430, 151), (425, 136)),
        BoardSlot((562, 131, 582, 151), (577, 136)),
        BoardSlot((714, 131, 734, 151), (729, 136)),
    ],
    rows=[
        BoardSlot((410, 395, 430, 415), (425, 401)),
        BoardSlot((562, 395, 582, 415), (577, 401)),
        BoardSlot((714, 395, 734, 415), (729, 401)),
        BoardSlot((866, 395, 886, 415), (881, 401)),
        BoardSlot((1018, 395, 1038, 415), (1033, 401)),
        BoardSlot((1170, 395, 1190, 415), (1185, 401)),
        BoardSlot((1322, 395, 1342, 415), (1337, 401)),
        BoardSlot((1474, 395, 1494, 415), (1489, 401)),
    ],
    dragons=[
        BoardSlot((0, 0, 0, 0), (890, 130)),
        BoardSlot((0, 0, 0, 0), (890, 240)),
        BoardSlot((0, 0, 0, 0), (890, 330)),
    ]

)
