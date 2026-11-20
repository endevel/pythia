import pytest

from pythia.core.board_size import BoardSize
from pythia.core.piece import Piece
from pythia.core.player import Player
from pythia.core.rank import Rank
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard


def test_default_board_dimensions():
    board = DamBoard()

    assert board.height == 8
    assert board.width == 8


def test_default_board_has_32_empty_squares():
    board = DamBoard()

    indices = list(board)

    assert len(indices) == 32
    assert all(board[ndx] == SquareState.EMPTY for ndx in indices)
    assert board.white_pieces == set()
    assert board.black_pieces == set()


def test_default_player_to_move_is_white():
    assert DamBoard().player_to_move == Player.WHITE


def test_getitem_returns_out_of_board_for_border():
    board = DamBoard()

    assert board[0] == SquareState.OUT_OF_BOARD
    assert board[9] == SquareState.OUT_OF_BOARD


def test_iteration_yields_squares_in_number_order():
    board = DamBoard()

    assert [board.number_at(ndx) for ndx in board] == list(range(1, 33))


def test_state_matches_getitem():
    board = DamBoard()
    ndx = next(iter(board))

    board.set_piece(Piece(Player.WHITE, square_ndx=1))

    assert board.state(ndx) == board[ndx] == SquareState.WHITE_MAN


def test_number_at_raises_for_non_playable_square():
    board = DamBoard()

    with pytest.raises(KeyError):
        board.number_at(0)


def test_set_piece_white_man():
    board = DamBoard()

    board.set_piece(Piece(Player.WHITE, square_ndx=1))

    ndx = next(iter(board))
    assert board[ndx] == SquareState.WHITE_MAN
    assert board.white_pieces == {1}
    assert board.black_pieces == set()


def test_set_piece_black_king():
    board = DamBoard()

    board.set_piece(Piece(Player.BLACK, Rank.KING, 32))

    ndx = list(board)[-1]
    assert board[ndx] == SquareState.BLACK_KING
    assert board.black_pieces == {32}
    assert board.white_pieces == set()


def test_remove_white_piece():
    board = DamBoard()
    board.set_piece(Piece(Player.WHITE, square_ndx=1))

    board.remove_piece(1)

    assert board.white_pieces == set()
    assert board.black_pieces == set()
    assert board[next(iter(board))] == SquareState.EMPTY


def test_remove_black_piece():
    board = DamBoard()
    board.set_piece(Piece(Player.BLACK, square_ndx=32))

    board.remove_piece(32)

    assert board.black_pieces == set()
    assert board.white_pieces == set()
    assert board[list(board)[-1]] == SquareState.EMPTY


def test_clear_removes_all_pieces():
    board = DamBoard()
    board.setup("B:W1,2:B31,32")

    board.clear()

    assert board.white_pieces == set()
    assert board.black_pieces == set()
    assert len(list(board)) == 32
    assert all(board[ndx] == SquareState.EMPTY for ndx in board)


def test_setup_sets_pieces_and_player_to_move():
    board = DamBoard()

    board.setup("B:W31,32:B1,2")

    indices = list(board)
    assert board.player_to_move == Player.BLACK
    assert board.white_pieces == {31, 32}
    assert board.black_pieces == {1, 2}
    assert board[indices[0]] == SquareState.BLACK_MAN
    assert board[indices[30]] == SquareState.WHITE_MAN
    assert board[indices[31]] == SquareState.WHITE_MAN


def test_setup_places_kings():
    board = DamBoard()

    board.setup("W:WK1:BK32")

    indices = list(board)
    assert board[indices[0]] == SquareState.WHITE_KING
    assert board[indices[-1]] == SquareState.BLACK_KING


def test_setup_replaces_previous_position():
    board = DamBoard()
    board.setup("W:W1:B32")

    board.setup("W:W2:B31")

    assert board.white_pieces == {2}
    assert board.black_pieces == {31}
    assert len(list(board)) == 32


def test_to_fen_for_empty_board():
    assert DamBoard().to_fen() == "W:W:B"


def test_to_fen_uses_given_start_color():
    board = DamBoard()
    board.setup("W:W31,32:B1,2")

    assert board.to_fen(Player.BLACK) == "B:W31,32:B1,2"


def test_to_fen_sorts_numbers_and_marks_kings():
    board = DamBoard()
    board.setup("W:W32,K1:B2,K31")

    assert board.to_fen() == "W:WK1,32:B2,K31"


def test_setup_and_to_fen_round_trip():
    board = DamBoard()
    position = "B:W31,32:B1,2"

    board.setup(position)

    assert board.to_fen(Player.BLACK) == position


@pytest.mark.parametrize(
    ("board_size", "height", "width", "playable_count"),
    [
        (BoardSize.STANDARD, 8, 8, 32),
        (BoardSize.BIG, 10, 10, 50),
        (BoardSize.LARGE, 12, 12, 72),
    ],
)
def test_board_size(board_size, height, width, playable_count):
    board = DamBoard(board_size=board_size)

    assert board.height == height
    assert board.width == width
    assert len(list(board)) == playable_count
    assert all(board[ndx] == SquareState.EMPTY for ndx in board)
    assert board[0] == SquareState.OUT_OF_BOARD


def test_custom_board_init_is_used():
    calls = []

    def board_init(board_size, squares, board_map):
        calls.append(board_size)
        squares.clear()
        board_map.clear()
        squares.extend([SquareState.EMPTY, SquareState.OUT_OF_BOARD])
        board_map.append(0)

    board = DamBoard(board_size=BoardSize.BIG, board_init=board_init)

    assert calls == [BoardSize.BIG]
    assert list(board) == [0]
    assert board.number_at(0) == 1
    assert board.height == 10

    board.clear()

    assert calls == [BoardSize.BIG, BoardSize.BIG]
    assert list(board) == [0]


def test_pieces_properties_return_new_sets():
    board = DamBoard()
    board.set_piece(Piece(Player.WHITE, square_ndx=1))
    board.set_piece(Piece(Player.BLACK, square_ndx=32))

    white = board.white_pieces
    black = board.black_pieces
    white.clear()
    black.clear()

    assert board.white_pieces == {1}
    assert board.black_pieces == {32}
