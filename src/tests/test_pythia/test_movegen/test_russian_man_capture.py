from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.russian_man_capture import RussianManCapture


def square_index(board: DamBoard, number: int) -> int:
    """Возвращает внутренний индекс плоского массива для номера поля."""

    for ndx in board:
        if board.number_at(ndx) == number:
            return ndx
    raise AssertionError(f"На доске нет поля {number}")


def make_board(position: str) -> DamBoard:
    board = DamBoard()
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
    before_state: SquareState,
    after_state: SquareState,
    taken: list[tuple[int, SquareState]],
) -> Move:
    """Собирает ожидаемый ударный ход простой шашки между номерами полей."""

    return Move(
        from_square=square_index(board, from_number),
        to_square=square_index(board, to_number),
        before_state=before_state,
        after_state=after_state,
        taken=[
            (square_index(board, number), taken_state) for number, taken_state in taken
        ],
    )


def test_man_without_opponent_has_no_captures():
    board = make_board("W:W22:B")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    assert moves == []


def test_white_man_captures_forward():
    board = make_board("W:W22:B18")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    assert moves == [
        capture_move(
            board,
            22,
            15,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(18, SquareState.BLACK_MAN)],
        )
    ]


def test_white_man_captures_backward():
    board = make_board("W:W22:B26")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    # В русских шашках простая бьёт и назад. Превращения нет, потому что
    # цепочка заканчивается вне дамочного ряда.
    assert moves == [
        capture_move(
            board,
            22,
            31,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(26, SquareState.BLACK_MAN)],
        )
    ]


def test_white_man_cannot_capture_own_piece():
    board = make_board("W:W22,18:B")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    assert moves == []


def test_white_man_can_capture_opponent_king():
    board = make_board("W:W22:BK18")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    assert moves == [
        capture_move(
            board,
            22,
            15,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(18, SquareState.BLACK_KING)],
        )
    ]


def test_white_man_promotes_when_chain_ends_on_last_row():
    board = make_board("W:W10:B6")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 10))

    # Шашка достигает дамочного ряда и не может бить дальше — превращается.
    assert moves == [
        capture_move(
            board,
            10,
            1,
            SquareState.WHITE_MAN,
            SquareState.WHITE_KING,
            [(6, SquareState.BLACK_MAN)],
        )
    ]


def test_white_man_continues_capture_as_king_after_promotion():
    board = make_board("W:W9:B6,11")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 9))

    # Шашка бьёт 6 и попадает на поле 2 (дамочный ряд). По правилам русских
    # шашек она сразу становится дамкой и продолжает бой уже на расстояние:
    # бьёт 11 и встаёт на любое свободное поле за ним.
    assert destinations(board, moves) == [16, 20]
    assert all(taken_numbers(board, move) == [6, 11] for move in moves)
    assert all(
        [state for _, state in move.taken]
        == [SquareState.BLACK_MAN, SquareState.BLACK_MAN]
        for move in moves
    )
    assert all(move.before_state is SquareState.WHITE_MAN for move in moves)
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)


def test_white_man_stays_man_when_chain_ends_off_last_row():
    board = make_board("W:W22:B18,10")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    # Цепочка не касается дамочного ряда, поэтому шашка остаётся простой.
    assert moves == [
        capture_move(
            board,
            22,
            6,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(18, SquareState.BLACK_MAN), (10, SquareState.BLACK_MAN)],
        )
    ]


def test_black_man_promotes_when_chain_ends_on_last_row():
    board = make_board("B:B22:W26")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 22))

    assert moves == [
        capture_move(
            board,
            22,
            31,
            SquareState.BLACK_MAN,
            SquareState.BLACK_KING,
            [(26, SquareState.WHITE_MAN)],
        )
    ]


def test_black_man_continues_capture_as_king_after_promotion():
    board = make_board("B:B21:W25,23")

    moves = RussianManCapture(board).generate_moves(board, square_index(board, 21))

    # Чёрная шашка бьёт 25, попадает на последний ряд, становится дамкой и
    # продолжает бой на расстояние: бьёт 23 с полей 19, 16 или 12.
    assert destinations(board, moves) == [12, 16, 19]
    assert all(taken_numbers(board, move) == [25, 23] for move in moves)
    assert all(
        [state for _, state in move.taken]
        == [SquareState.WHITE_MAN, SquareState.WHITE_MAN]
        for move in moves
    )
    assert all(move.before_state is SquareState.BLACK_MAN for move in moves)
    assert all(move.after_state is SquareState.BLACK_KING for move in moves)
