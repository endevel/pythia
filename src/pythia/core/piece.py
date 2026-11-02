from pythia.core import Player, Rank


class Piece:
    """Representation of a piece on the board."""

    def __init__(self, owner: Player, square_ndx: int):
        self.__owner = owner
        self.__square_ndx = square_ndx
        self.__rank = Rank.MAN

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
