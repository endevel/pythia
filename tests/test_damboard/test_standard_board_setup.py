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


def test_setup_midgame_position_with_kings():
    # Миттельшпильная позиция: у обеих сторон есть дамка и простые шашки.
    # Белая дамка прошла в первую горизонталь (клетка 1),
    # чёрная дамка достигла последней горизонтали (клетка 30).
    board = Damboard()
    board.setup("B:WK1,25,27,32:BK30,19,21,23.")

    assert len(board.white_pieces) == 4
    assert len(board.black_pieces) == 4

    # Белые: дамка на клетке 1, простые на клетках 25, 27, 32
    assert board[12] == SquareState.WHITE_KING
    assert board[72] == SquareState.WHITE_MAN
    assert board[76] == SquareState.WHITE_MAN
    assert board[87] == SquareState.WHITE_MAN

    # Чёрные: дамка на клетке 30, простые на клетках 19, 21, 23
    assert board[83] == SquareState.BLACK_KING
    assert board[56] == SquareState.BLACK_MAN
    assert board[61] == SquareState.BLACK_MAN
    assert board[65] == SquareState.BLACK_MAN

    # Свободные клетки 2 и 26
    assert board[14] == SquareState.EMPTY
    assert board[74] == SquareState.EMPTY


def test_setup_endgame_position():
    # Эндшпиль: белые имеют дамку (клетка 2) и две простые (26, 30),
    # чёрные - дамку (клетка 31) и одну простую (19).
    board = Damboard()
    board.setup("W:WK2,26,30:BK31,19.")

    assert len(board.white_pieces) == 3
    assert len(board.black_pieces) == 2

    assert board[14] == SquareState.WHITE_KING
    assert board[74] == SquareState.WHITE_MAN
    assert board[83] == SquareState.WHITE_MAN

    assert board[85] == SquareState.BLACK_KING
    assert board[56] == SquareState.BLACK_MAN

    # Остальные клетки пусты
    assert board[12] == SquareState.EMPTY
    assert board[18] == SquareState.EMPTY
    assert board[87] == SquareState.EMPTY


def test_setup_position_with_kings_on_both_sides():
    # Оживлённая позиция из миттельшпиля: 12 фигур у каждой стороны,
    # у белых дамка на клетке 2, у чёрных - на клетке 31.
    board = Damboard()
    board.setup("W:WK2,25,26,27,28,29,30,19,21,23,24,22:BK31,1,3,4,5,6,7,8,9,10,11,12.")

    assert len(board.white_pieces) == 12
    assert len(board.black_pieces) == 12

    assert board[14] == SquareState.WHITE_KING
    assert board[85] == SquareState.BLACK_KING

    assert board[72] == SquareState.WHITE_MAN
    assert board[78] == SquareState.WHITE_MAN
    assert board[81] == SquareState.WHITE_MAN
    assert board[56] == SquareState.WHITE_MAN
    assert board[67] == SquareState.WHITE_MAN

    assert board[12] == SquareState.BLACK_MAN
    assert board[18] == SquareState.BLACK_MAN
    assert board[25] == SquareState.BLACK_MAN
    assert board[38] == SquareState.BLACK_MAN

    # Клетки 20 и 32 свободны
    assert board[58] == SquareState.EMPTY
    assert board[87] == SquareState.EMPTY


def test_setup_replaces_previous_position():
    # Повторный setup должен полностью заменить предыдущую позицию,
    # включая снятие фигур, которых нет в новой позиции.
    board = Damboard()
    board.setup("W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12.")
    assert len(board.white_pieces) == 12
    assert len(board.black_pieces) == 12

    board.setup("B:WK1,25,27,32:BK30,19,21,23.")
    assert len(board.white_pieces) == 4
    assert len(board.black_pieces) == 4

    assert board[12] == SquareState.WHITE_KING
    assert board[83] == SquareState.BLACK_KING
    assert board[61] == SquareState.BLACK_MAN
    # Клетки, занятые в начальной расстановке, теперь пусты
    assert board[63] == SquareState.EMPTY
    assert board[14] == SquareState.EMPTY
