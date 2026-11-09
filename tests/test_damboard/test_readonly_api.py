from pythia.core.square_state import SquareState
from pythia.damboard.damboard import Damboard


def test_state_by_internal_index():
    board = Damboard()
    assert board.state(0) == SquareState.OUT_OF_BOARD
    assert board.state(72) == SquareState.EMPTY


def test_number_at_reverse_map():
    board = Damboard()
    # Итератор отдаёт внутренние индексы игровых полей.
    # Обратное отображение должно покрывать номера 1..N без пропусков.
    numbers = [board.number_at(ndx) for ndx in board]
    assert sorted(numbers) == list(range(1, board.height * board.width // 2 + 1))


def test_number_at_after_clear():
    board = Damboard()
    board.clear()
    numbers = [board.number_at(ndx) for ndx in board]
    assert sorted(numbers) == list(range(1, board.height * board.width // 2 + 1))


def test_piece_lists_return_square_numbers():
    board = Damboard()
    board.setup("B:WK1,25,27,32:BK30,19,21,23.")

    assert board.white_pieces == {1, 25, 27, 32}
    assert board.black_pieces == {30, 19, 21, 23}


def test_piece_lists_track_removal():
    board = Damboard()
    board.setup("W:W25:B1.")
    assert board.white_pieces == {25}

    board.remove_piece(25)
    assert board.white_pieces == set()
