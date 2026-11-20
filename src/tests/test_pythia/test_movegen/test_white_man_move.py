from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.white_man_move import WhiteManMove


def square_index(board: DamBoard, number: int) -> int:
    """Возвращает внутренний индекс плоского массива для номера поля."""

    for ndx in board:
        if board.number_at(ndx) == number:
            return ndx
    raise AssertionError(f"На доске нет поля {number}")


def make_board(position: str, board_size: BoardSize = BoardSize.STANDARD) -> DamBoard:
    board = DamBoard(board_size=board_size)
    board.setup(position)
    return board


def destinations(board: DamBoard, moves: list[Move]) -> list[int]:
    return sorted(board.number_at(move.to_square) for move in moves)


def test_white_man_moves_forward_right():
    board = make_board("W:W21:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [17]


def test_white_man_moves_forward_left_and_right():
    board = make_board("W:W22:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 22))

    assert destinations(board, moves) == [17, 18]


def test_move_contains_indices_and_piece_state():
    board = make_board("W:W22:B")
    from_ndx = square_index(board, 22)

    moves = WhiteManMove(board).generate_moves(board, from_ndx)

    assert moves == [
        Move(
            from_square=from_ndx,
            to_square=square_index(board, 18),
            before_state=SquareState.WHITE_MAN,
            after_state=SquareState.WHITE_MAN,
        ),
        Move(
            from_square=from_ndx,
            to_square=square_index(board, 17),
            before_state=SquareState.WHITE_MAN,
            after_state=SquareState.WHITE_MAN,
        ),
    ]


def test_white_man_cannot_move_off_the_board():
    board = make_board("W:W1:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 1))

    assert moves == []


def test_white_man_cannot_move_onto_occupied_square():
    board = make_board("W:W21,17:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 21))

    assert moves == []


def test_white_man_can_use_single_free_diagonal():
    board = make_board("W:W22,17:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 22))

    assert destinations(board, moves) == [18]


def test_white_man_moves_on_big_board():
    board = make_board("W:W46:B", BoardSize.BIG)

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 46))

    assert destinations(board, moves) == [41]


def test_white_man_promotes_on_last_row():
    board = make_board("W:W6:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 6))

    assert destinations(board, moves) == [1, 2]
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)


def test_white_man_keeps_rank_off_last_row():
    board = make_board("W:W14:B")

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 14))

    assert destinations(board, moves) == [9, 10]
    assert all(move.after_state is SquareState.WHITE_MAN for move in moves)


def test_white_man_promotes_on_big_board():
    board = make_board("W:W7:B", BoardSize.BIG)

    moves = WhiteManMove(board).generate_moves(board, square_index(board, 7))

    assert destinations(board, moves) == [1, 2]
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)
