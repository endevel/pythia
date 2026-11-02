from pythia.core import SquareState
from pythia.damboard.damboard import Damboard


def test_standard_board_create():
    board = Damboard()
    for i in range(0, 11):
        assert board[i] == SquareState.OUT_OF_BOARD

    for square in board:
        assert board[square] == SquareState.EMPTY
