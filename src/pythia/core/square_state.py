from enum import Enum


class SquareState(Enum):
    """Representation lof the state of a board square.""

    Args:
        Enum (_type_): _description_
    """

    EMPTY = 0
    WHITE_PIECE = 1
    WHITE_KING = 2
    BLACK_PIECE = 3
    BLACK_KING = 4
    TAKEN = 5
    OUT_OF_BOARD = 6
