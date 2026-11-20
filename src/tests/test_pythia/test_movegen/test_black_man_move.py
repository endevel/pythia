from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.black_man_move import BlackManMove


def square_index(board: DamBoard, number: int) -> int:
    """Возвращает внутренний индекс плоского массива для номера поля."""

    for ndx in board:
        if board.number_at(ndx) == number:
            return ndx
    raise AssertionError(f"На доске нет поля {number}")


def make_board(
    position: str, board_size: BoardSize = BoardSize.STANDARD
) -> DamBoard:
    board = DamBoard(board_size=board_size)
    board.setup(position)
    return board


def destinations(board: DamBoard, moves: list[Move]) -> list[int]:
    return sorted(board.number_at(move.to_square) for move in moves)


def test_black_man_moves_forward():
    board = make_board("B:B12:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 12))

    assert destinations(board, moves) == [16]


def test_black_man_moves_forward_left_and_right():
    board = make_board("B:B11:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 11))

    assert destinations(board, moves) == [15, 16]


def test_move_contains_indices_and_piece_state():
    board = make_board("B:B11:W")
    from_ndx = square_index(board, 11)

    moves = BlackManMove(board).generate_moves(board, from_ndx)

    assert moves == [
        Move(
            from_square=from_ndx,
            to_square=square_index(board, 16),
            before_state=SquareState.BLACK_MAN,
            after_state=SquareState.BLACK_MAN,
        ),
        Move(
            from_square=from_ndx,
            to_square=square_index(board, 15),
            before_state=SquareState.BLACK_MAN,
            after_state=SquareState.BLACK_MAN,
        ),
    ]


def test_black_man_cannot_move_off_the_board():
    board = make_board("B:B29:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 29))

    assert moves == []


def test_black_man_cannot_move_onto_occupied_square():
    board = make_board("B:B12,16:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 12))

    assert moves == []


def test_black_man_can_use_single_free_diagonal():
    board = make_board("B:B11,16:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 11))

    assert destinations(board, moves) == [15]


def test_black_man_moves_on_big_board():
    board = make_board("B:B5:W", BoardSize.BIG)

    moves = BlackManMove(board).generate_moves(board, square_index(board, 5))

    assert destinations(board, moves) == [10]


def test_black_man_promotes_on_last_row():
    board = make_board("B:B25:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 25))

    assert destinations(board, moves) == [29, 30]
    assert all(move.after_state is SquareState.BLACK_KING for move in moves)


def test_black_man_keeps_rank_off_last_row():
    board = make_board("B:B19:W")

    moves = BlackManMove(board).generate_moves(board, square_index(board, 19))

    assert destinations(board, moves) == [23, 24]
    assert all(move.after_state is SquareState.BLACK_MAN for move in moves)


def test_black_man_promotes_on_big_board():
    board = make_board("B:B44:W", BoardSize.BIG)

    moves = BlackManMove(board).generate_moves(board, square_index(board, 44))

    assert destinations(board, moves) == [49, 50]
    assert all(move.after_state is SquareState.BLACK_KING for move in moves)
