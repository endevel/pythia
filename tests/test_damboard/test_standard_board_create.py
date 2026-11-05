from pythia.core import SquareState
from pythia.core.piece import Piece
from pythia.core.player import Player
from pythia.core.rank import Rank
from pythia.damboard.damboard import Damboard


def test_standard_board_create():
    board = Damboard()
    assert board.height == 8
    assert board.width == 8
    for i in range(0, 11):
        assert board[i] == SquareState.OUT_OF_BOARD

    for square in board:
        assert board[square] == SquareState.EMPTY


def test_set_piece_on_square():
    board = Damboard()
    piece = Piece(Player.WHITE, Rank.MAN, 25)
    board.set_piece(piece)
    assert board[72] == SquareState.WHITE_MAN


def test_remove_piece_from_square():
    board = Damboard()
    piece = Piece(Player.WHITE, Rank.MAN, 25)
    board.set_piece(piece)
    assert board[72] == SquareState.WHITE_MAN
    board.remove_piece(25)
    assert board[72] == SquareState.EMPTY
