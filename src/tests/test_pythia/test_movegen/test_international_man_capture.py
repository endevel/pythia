from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.standard.international_man_capture import (
    InternationalManCapture,
)


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
            (square_index(board, number), taken_state)
            for number, taken_state in taken
        ],
    )


def test_man_without_opponent_has_no_captures():
    board = make_board("W:W22:B")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

    assert moves == []


def test_white_man_captures_forward():
    board = make_board("W:W22:B18")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

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

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

    # По международным правилам простая бьёт и назад, но превращается
    # только на своём дамочном ряду, поэтому здесь она остаётся простой.
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

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

    assert moves == []


def test_white_man_can_capture_opponent_king():
    board = make_board("W:W22:BK18")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

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


def test_white_man_promotes_when_cannot_continue_on_last_row():
    board = make_board("W:W10:B6")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 10)
    )

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


def test_white_man_continues_capture_on_last_row_and_stays_man():
    board = make_board("W:W9:B6,7")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 9)
    )

    # Достигнув дамочного ряда, шашка обязана продолжить бой как простая.
    # Цепочка заканчивается вне дамочного ряда, поэтому дамкой она не стала.
    assert moves == [
        capture_move(
            board,
            9,
            11,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(6, SquareState.BLACK_MAN), (7, SquareState.BLACK_MAN)],
        )
    ]


def test_white_man_promotes_when_chain_ends_on_last_row():
    board = make_board("W:W18:B14,6")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 18)
    )

    assert destinations(board, moves) == [2]
    assert taken_numbers(board, moves[0]) == [14, 6]
    assert moves[0].before_state is SquareState.WHITE_MAN
    assert moves[0].after_state is SquareState.WHITE_KING


def test_black_man_captures_backward():
    board = make_board("B:B22:W18")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

    assert moves == [
        capture_move(
            board,
            22,
            15,
            SquareState.BLACK_MAN,
            SquareState.BLACK_MAN,
            [(18, SquareState.WHITE_MAN)],
        )
    ]


def test_black_man_promotes_on_last_row():
    board = make_board("B:B22:W26")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 22)
    )

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


def test_black_man_continues_capture_and_stays_man():
    board = make_board("B:B24:W27,26")

    moves = InternationalManCapture(board).generate_moves(
        board, square_index(board, 24)
    )

    # Чёрная шашка доходит до последнего ряда и продолжает бой как простая,
    # заканчивая цепочку вне дамочного ряда.
    assert moves == [
        capture_move(
            board,
            24,
            22,
            SquareState.BLACK_MAN,
            SquareState.BLACK_MAN,
            [(27, SquareState.WHITE_MAN), (26, SquareState.WHITE_MAN)],
        )
    ]
