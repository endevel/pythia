from pythia.core.move import Move
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.russian_move_gen import RussianMoveGen


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


def make_move(
    board: DamBoard,
    from_number: int,
    to_number: int,
    before_state: SquareState,
    after_state: SquareState,
    taken: list[tuple[int, SquareState]] | None = None,
) -> Move:
    """Собирает ожидаемый ход между номерами полей."""

    return Move(
        from_square=square_index(board, from_number),
        to_square=square_index(board, to_number),
        before_state=before_state,
        after_state=after_state,
        taken=[
            (square_index(board, number), taken_state)
            for number, taken_state in taken or []
        ],
    )


def test_white_man_has_quiet_moves_when_no_captures():
    board = make_board("W:W22:B")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    assert destinations(board, moves) == [17, 18]
    assert all(move.taken == [] for move in moves)


def test_black_man_has_quiet_moves_when_no_captures():
    board = make_board("B:B22:W")

    moves = RussianMoveGen(board, Player.BLACK).generate_move_list()

    assert destinations(board, moves) == [25, 26]
    assert all(move.taken == [] for move in moves)


def test_white_man_promotes_on_quiet_move():
    board = make_board("W:W5:B")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    assert moves == [
        make_move(
            board,
            5,
            1,
            SquareState.WHITE_MAN,
            SquareState.WHITE_KING,
        )
    ]


def test_white_king_has_quiet_moves_when_no_captures():
    board = make_board("W:WK21:B")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    assert destinations(board, moves) == [3, 7, 10, 14, 17, 25, 30]
    assert all(move.taken == [] for move in moves)


def test_man_capture_is_mandatory():
    board = make_board("W:W22:B18")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    # Тихий ход 22-17 существует, но при наличии взятия он недопустим.
    assert moves == [
        make_move(
            board,
            22,
            15,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(18, SquareState.BLACK_MAN)],
        )
    ]


def test_king_capture_is_mandatory():
    board = make_board("W:WK21:B17")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    # Тихие ходы дамки (25 и 30) не возвращаются, пока возможно взятие.
    assert destinations(board, moves) == [3, 7, 10, 14]
    assert all(move.taken != [] for move in moves)


def test_man_captures_backward():
    board = make_board("W:W22:B26")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    assert moves == [
        make_move(
            board,
            22,
            31,
            SquareState.WHITE_MAN,
            SquareState.WHITE_MAN,
            [(26, SquareState.BLACK_MAN)],
        )
    ]


def test_black_man_capture_uses_russian_rules():
    board = make_board("B:B22:W18")

    moves = RussianMoveGen(board, Player.BLACK).generate_move_list()

    assert moves == [
        make_move(
            board,
            22,
            15,
            SquareState.BLACK_MAN,
            SquareState.BLACK_MAN,
            [(18, SquareState.WHITE_MAN)],
        )
    ]


def test_all_captures_are_returned_without_maximum_filter():
    board = make_board("W:W22,28:B18,10,24")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    # В русских шашках игрок вправе выбрать любой бой. Шашка 22 снимает
    # две фигуры, шашка 28 — одну, и оба хода должны быть возвращены.
    by_from = {board.number_at(move.from_square): move for move in moves}
    assert set(by_from) == {22, 28}
    assert board.number_at(by_from[22].to_square) == 6
    assert taken_numbers(board, by_from[22]) == [18, 10]
    assert board.number_at(by_from[28].to_square) == 19
    assert taken_numbers(board, by_from[28]) == [24]


def test_man_promotes_and_continues_capture_as_king():
    board = make_board("W:W9:B6,11")

    moves = RussianMoveGen(board, Player.WHITE).generate_move_list()

    # Шашка бьёт 6, попадает на дамочный ряд, становится дамкой и
    # продолжает бой на расстояние, снимая 11.
    assert destinations(board, moves) == [16, 20]
    assert all(taken_numbers(board, move) == [6, 11] for move in moves)
    assert all(move.before_state is SquareState.WHITE_MAN for move in moves)
    assert all(move.after_state is SquareState.WHITE_KING for move in moves)


def test_generator_uses_given_player_not_fen_color():
    board = make_board("B:W22:B18")

    moves = RussianMoveGen(board, Player.BLACK).generate_move_list()

    # Ход чёрных: бьёт чёрная шашка 18, а не белая 22, несмотря на FEN.
    assert [board.number_at(move.from_square) for move in moves] == [18]
    assert destinations(board, moves) == [25]
