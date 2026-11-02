from enum import Enum


class BoardSize(Enum):
    STANDARD = 0
    BIG = 1
    LARGE = 2

    @property
    def height(self):
        return 8 if self == BoardSize.STANDARD else 10 if self == BoardSize.BIG else 12

    @property
    def width(self):
        return 8 if self == BoardSize.STANDARD else 10 if self == BoardSize.BIG else 12
