from pythia.core.piece import Piece
from pythia.core.player import Player


def test_default_create():

    piece = Piece(Player.WHITE)
    assert piece is not None
    assert isinstance(piece, Piece)
    assert piece.owner == Player.WHITE
    assert piece.rank.name == "MAN"
    assert piece.square_ndx == 0
