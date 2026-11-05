from pythia.core.square_state import SquareState
from pythia.damboard.damboard import Damboard


def test_setup_start_position():
    board = Damboard()
    board.setup("W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12.")
    assert len(board.white_pieces) == 12
    assert len(board.black_pieces) == 12
    assert board[61] == SquareState.WHITE_MAN
    assert board[63] == SquareState.WHITE_MAN    
    assert board[65] == SquareState.WHITE_MAN
    assert board[67] == SquareState.WHITE_MAN
    assert board[72] == SquareState.WHITE_MAN
    assert board[74] == SquareState.WHITE_MAN
    assert board[76] == SquareState.WHITE_MAN
    assert board[78] == SquareState.WHITE_MAN
    assert board[81] == SquareState.WHITE_MAN
    assert board[83] == SquareState.WHITE_MAN
    assert board[85] == SquareState.WHITE_MAN
    assert board[87] == SquareState.WHITE_MAN
    
    assert board[12] == SquareState.BLACK_MAN
    assert board[14] == SquareState.BLACK_MAN    
    assert board[16] == SquareState.BLACK_MAN
    assert board[18] == SquareState.BLACK_MAN
    assert board[21] == SquareState.BLACK_MAN
    assert board[23] == SquareState.BLACK_MAN
    assert board[25] == SquareState.BLACK_MAN
    assert board[27] == SquareState.BLACK_MAN
    assert board[32] == SquareState.BLACK_MAN
    assert board[34] == SquareState.BLACK_MAN
    assert board[36] == SquareState.BLACK_MAN
    assert board[38] == SquareState.BLACK_MAN
    