from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.king_move import KingMove


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


def king_move(
    board: DamBoard, from_number: int, to_number: int, state: SquareState
) -> Move:
    """Собирает ожидаемый тихий ход дамки между номерами полей."""

    return Move(
        from_square=square_index(board, from_number),
        to_square=square_index(board, to_number),
        before_state=state,
        after_state=state,
    )


def test_white_king_moves_along_all_diagonals():
    board = make_board("W:WK21:B")

    moves = KingMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7, 10, 14, 17, 25, 30]


def test_black_king_moves_exactly_like_white_king():
    board = make_board("B:BK21:W")

    moves = KingMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7, 10, 14, 17, 25, 30]


def test_king_move_contains_indices_and_piece_state():
    board = make_board("W:WK22:B")
    state = SquareState.WHITE_KING

    moves = KingMove(board).generate_moves(board, square_index(board, 22))

    assert moves == [
        king_move(board, 22, 17, state),
        king_move(board, 22, 13, state),
        king_move(board, 22, 18, state),
        king_move(board, 22, 15, state),
        king_move(board, 22, 11, state),
        king_move(board, 22, 8, state),
        king_move(board, 22, 4, state),
        king_move(board, 22, 25, state),
        king_move(board, 22, 29, state),
        king_move(board, 22, 26, state),
        king_move(board, 22, 31, state),
    ]


def test_king_cannot_move_off_the_board():
    board = make_board("W:WK1:B")

    moves = KingMove(board).generate_moves(board, square_index(board, 1))

    assert destinations(board, moves) == [5, 6, 10, 15, 19, 24, 28]


def test_king_stops_before_own_piece():
    board = make_board("W:WK21,17:B")

    moves = KingMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [25, 30]


def test_king_stops_before_opponent_piece():
    board = make_board("W:WK21:B17")

    moves = KingMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [25, 30]


def test_king_keeps_rank():
    board = make_board("W:WK22:B")

    moves = KingMove(board).generate_moves(board, square_index(board, 22))

    assert all(move.before_state is SquareState.WHITE_KING for move in moves)
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)


def test_king_moves_on_big_board():
    board = make_board("W:WK21:B", BoardSize.BIG)

    moves = KingMove(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 8, 12, 16, 17, 26, 27, 32, 38, 43, 49]
