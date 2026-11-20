from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.king_capture import KingCapture


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


def taken_numbers(board: DamBoard, move: Move) -> list[int]:
    return [board.number_at(ndx) for ndx, _ in move.taken]


def capture_move(
    board: DamBoard,
    from_number: int,
    to_number: int,
    state: SquareState,
    taken: list[tuple[int, SquareState]],
) -> Move:
    """Собирает ожидаемый ударный ход дамки между номерами полей."""

    return Move(
        from_square=square_index(board, from_number),
        to_square=square_index(board, to_number),
        before_state=state,
        after_state=state,
        taken=[
            (square_index(board, number), taken_state)
            for number, taken_state in taken
        ],
    )


def test_king_without_opponent_has_no_captures():
    board = make_board("W:WK21:B")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert moves == []


def test_king_captures_opponent_and_lands_on_any_free_square():
    board = make_board("W:WK21:B17")
    state = SquareState.WHITE_KING

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7, 10, 14]
    assert moves == [
        capture_move(board, 21, 14, state, [(17, SquareState.BLACK_MAN)]),
        capture_move(board, 21, 10, state, [(17, SquareState.BLACK_MAN)]),
        capture_move(board, 21, 7, state, [(17, SquareState.BLACK_MAN)]),
        capture_move(board, 21, 3, state, [(17, SquareState.BLACK_MAN)]),
    ]


def test_black_king_captures_exactly_like_white_king():
    board = make_board("B:BK21:W17")
    state = SquareState.BLACK_KING

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7, 10, 14]
    assert moves == [
        capture_move(board, 21, 14, state, [(17, SquareState.WHITE_MAN)]),
        capture_move(board, 21, 10, state, [(17, SquareState.WHITE_MAN)]),
        capture_move(board, 21, 7, state, [(17, SquareState.WHITE_MAN)]),
        capture_move(board, 21, 3, state, [(17, SquareState.WHITE_MAN)]),
    ]


def test_king_can_capture_opponent_king():
    board = make_board("W:WK21:BK17")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7, 10, 14]
    assert all(
        move.taken == [(square_index(board, 17), SquareState.BLACK_KING)]
        for move in moves
    )


def test_king_cannot_capture_own_piece():
    board = make_board("W:WK21,17:B")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert moves == []


def test_king_cannot_jump_over_own_piece_to_opponent():
    board = make_board("W:WK21,17:B10")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert moves == []


def test_king_without_opponent_on_diagonal_has_no_captures():
    board = make_board("W:WK21:B22")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert moves == []


def test_king_captures_several_pieces_in_one_move():
    board = make_board("W:WK21:B17,10")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 7]
    assert all(taken_numbers(board, move) == [17, 10] for move in moves)
    assert all(
        [state for _, state in move.taken]
        == [SquareState.BLACK_MAN, SquareState.BLACK_MAN]
        for move in moves
    )


def test_king_cannot_pass_over_taken_piece():
    board = make_board("W:WK14:B17,7")

    moves = KingCapture(board).generate_moves(board, square_index(board, 14))

    assert destinations(board, moves) == [3, 21]
    # Дамка не может перепрыгнуть уже взятую фигуру и собрать обе шашки.
    assert sorted(taken_numbers(board, move) for move in moves) == [[7], [17]]


def test_king_chooses_between_capture_directions():
    board = make_board("W:WK14:B17,10")

    moves = KingCapture(board).generate_moves(board, square_index(board, 14))

    assert destinations(board, moves) == [3, 7, 21]
    assert sorted(taken_numbers(board, move) for move in moves) == [
        [10],
        [10],
        [17],
    ]


def test_king_move_records_taken_state_and_keeps_rank():
    board = make_board("W:WK21:B17")

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert all(move.before_state is SquareState.WHITE_KING for move in moves)
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)
    assert all(move.from_square == square_index(board, 21) for move in moves)
    assert all(
        move.taken == [(square_index(board, 17), SquareState.BLACK_MAN)]
        for move in moves
    )


def test_king_captures_on_big_board():
    board = make_board("W:WK21:B17", BoardSize.BIG)

    moves = KingCapture(board).generate_moves(board, square_index(board, 21))

    assert destinations(board, moves) == [3, 8, 12]
    assert all(taken_numbers(board, move) == [17] for move in moves)
