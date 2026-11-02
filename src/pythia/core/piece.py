from pythia.core import Player, Rank


class Piece:
    """Representation of a piece on the board."""

    def __init__(self, owner: Player, square_ndx: int):
        self.__owner = owner
        self.__square_ndx = square_ndx
        self.__rank = Rank.MAN

    @property
    def owner(self) -> Player:
        return self.__owner

    @property
    def square_ndx(self) -> int:
        return self.__square_ndx

    @property
    def rank(self) -> Rank:
        return self.__rank
