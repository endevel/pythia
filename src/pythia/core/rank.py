from enum import Enum


class Rank(Enum):
    """Representation of the rank of a piece.

    Args:
        Enum (_type_): _description_
    """

    MAN = 0
    KING = 1

    def promote(self):
        """Promotes a piece to a king.

        Returns:
            Rank: The rank of the piece after promotion.
        """
        return Rank.KING if self == Rank.MAN else Rank.KING
