from pythia.core import Player, Rank
from pythia.core.square_state import SquareState


class Piece:
    """Representation of a piece on the board."""

    def __init__(self, owner: Player, rank: Rank = Rank.MAN, square_ndx: int = 0):
        self.__owner = owner
        self.__square_ndx = square_ndx
        self.__rank = rank

    def change_owner(self):
        if self.__owner == Player.WHITE:
            self.__owner = Player.BLACK
        else:
            self.__owner = Player.WHITE

    def promote(self):
        if self.__rank == Rank.MAN:
            self.__rank = Rank.KING

    def set_square_ndx(self, square_ndx: int):
        self.__square_ndx = square_ndx

    @property
    def owner(self) -> Player:
        return self.__owner

    @property
    def square_ndx(self) -> int:
        return self.__square_ndx

    @property
    def rank(self) -> Rank:
        return self.__rank

    @property
    def square_state(self) -> SquareState:
        if self.__owner == Player.WHITE:
            if self.__rank == Rank.MAN:
                return SquareState.WHITE_MAN
            else:
                return SquareState.WHITE_KING
        else:
            if self.__rank == Rank.MAN:
                return SquareState.BLACK_MAN
            else:
                return SquareState.BLACK_KING
