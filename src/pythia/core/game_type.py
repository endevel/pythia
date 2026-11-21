from enum import Enum

from pythia.core.board_size import BoardSize
from pythia.core.rules import Rules

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
    def rules(self) -> Rules:
        if self == GameType.BRAZILIAN:
            return Rules.INTERNATIONAL
        elif self == GameType.INTERNATIONAL:
            return Rules.INTERNATIONAL
        elif self == GameType.RUSSIAN:
            return Rules.RUSSIAN
        else:
            raise ValueError("Invalid game type")
