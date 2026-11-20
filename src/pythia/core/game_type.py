from enum import Enum

from pythia.damboard.board_size import BoardSize
from pythia.movegen.rules import RUSSIAN, INTERNATIONAL


class GameType(Enum):
    BRAZILIAN = (0,)
    INTERNATIONAL = (1,)
    RUSSIAN = (2,)

    @property
    def board_size(self):
        if self == GameType.BRAZILIAN:
            return BoardSize.STANDARD
        elif self == GameType.INTERNATIONAL:
            return BoardSize.BIG
        elif self == GameType.RUSSIAN:
            return BoardSize.STANDARD

    @property
    def rules(self):
        if self == GameType.BRAZILIAN:
            return RUSSIAN
        elif self == GameType.INTERNATIONAL:
            return INTERNATIONAL
        elif self == GameType.RUSSIAN:
            return RUSSIAN
