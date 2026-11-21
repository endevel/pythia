from pythia.core.move import Move, move_to_str
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard


def make_move(
    board: DamBoard,
    from_number: int,
    to_number: int,
    taken_numbers: tuple[int, ...] = (),
    path_numbers: tuple[int, ...] | None = None,
) -> Move:
    """Собирает ход между номерами полей для проверки печати."""

    return Move(
        from_square=board.ndx_of_number(from_number),
        to_square=board.ndx_of_number(to_number),
        before_state=SquareState.WHITE_MAN,
        after_state=SquareState.WHITE_MAN,
        taken=[
            (board.ndx_of_number(number), SquareState.BLACK_MAN)
            for number in taken_numbers
        ],
        path=tuple(
            board.ndx_of_number(number) for number in (path_numbers or ())
        ),
    )


def test_quiet_move_is_printed_with_dash():
    board = DamBoard()
    move = make_move(board, 32, 28, path_numbers=(32, 28))

    assert move_to_str(move, board) == "32-28"


def test_capture_is_printed_with_x():
    board = DamBoard()
    move = make_move(board, 22, 15, taken_numbers=(18,), path_numbers=(22, 15))

    assert move_to_str(move, board) == "22x15"


def test_multi_capture_prints_intermediate_landing_squares():
    board = DamBoard()
    move = make_move(
        board,
        22,
        6,
        taken_numbers=(18, 10),
        path_numbers=(22, 15, 6),
    )

    assert move_to_str(move, board) == "22x15x6"


def test_capture_without_path_prints_end_squares():
    board = DamBoard()
    move = make_move(board, 22, 15, taken_numbers=(18,))

    assert move_to_str(move, board) == "22x15"


def test_path_inconsistent_with_end_squares_is_ignored():
    board = DamBoard()
    move = make_move(board, 22, 15, path_numbers=(32, 28))

    assert move_to_str(move, board) == "22-15"
