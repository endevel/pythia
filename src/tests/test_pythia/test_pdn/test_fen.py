import pytest

from pythia.core.player import Player
from pythia.core.rank import Rank
from pythia.core.square_state import SquareState
from pythia.pdn.fen import Fen, fen_from_states


def plus_one(ndx: int) -> int:
    return ndx + 1


def test_fen_from_states_empty_position_white_to_move():
    assert fen_from_states({}, plus_one, Player.WHITE) == "W:W:B"


def test_fen_from_states_empty_position_black_to_move():
    assert fen_from_states({}, plus_one, Player.BLACK) == "B:W:B"


def test_fen_from_states_white_men():
    states = {0: SquareState.WHITE_MAN, 1: SquareState.WHITE_MAN}

    assert fen_from_states(states, plus_one, Player.WHITE) == "W:W1,2:B"


def test_fen_from_states_black_men():
    states = {0: SquareState.BLACK_MAN, 1: SquareState.BLACK_MAN}

    assert fen_from_states(states, plus_one, Player.WHITE) == "W:W:B1,2"


def test_fen_from_states_marks_kings():
    states = {0: SquareState.WHITE_KING, 1: SquareState.BLACK_KING}

    assert fen_from_states(states, plus_one, Player.WHITE) == "W:WK1:BK2"


def test_fen_from_states_uses_number_of_for_square_numbers():
    numbers = {10: 32, 20: 1}
    states = {10: SquareState.WHITE_MAN, 20: SquareState.BLACK_MAN}

    assert (
        fen_from_states(states, numbers.__getitem__, Player.WHITE) == "W:W32:B1"
    )


def test_fen_from_states_sorts_by_square_number():
    numbers = {0: 32, 1: 1, 2: 31, 3: 2}
    states = {
        0: SquareState.WHITE_MAN,
        1: SquareState.WHITE_KING,
        2: SquareState.BLACK_MAN,
        3: SquareState.BLACK_KING,
    }

    assert (
        fen_from_states(states, numbers.__getitem__, Player.BLACK)
        == "B:WK1,32:BK2,31"
    )


@pytest.mark.parametrize(
    "state",
    [
        SquareState.EMPTY,
        SquareState.TAKEN,
        SquareState.OUT_OF_BOARD,
    ],
)
def test_fen_from_states_skips_non_piece_states(state):
    calls = []

    def number_of(ndx):
        calls.append(ndx)
        return ndx + 1

    assert fen_from_states({0: state}, number_of, Player.WHITE) == "W:W:B"
    assert calls == []


def test_fen_from_states_calls_number_of_only_for_pieces():
    calls = []

    def number_of(ndx):
        calls.append(ndx)
        return ndx + 1

    states = {
        0: SquareState.EMPTY,
        1: SquareState.WHITE_MAN,
        2: SquareState.TAKEN,
        3: SquareState.BLACK_KING,
        4: SquareState.OUT_OF_BOARD,
    }

    fen_from_states(states, number_of, Player.WHITE)

    assert calls == [1, 3]


def test_fen_default_is_empty_with_white_to_move():
    fen = Fen()

    assert fen.player_to_move == Player.WHITE
    assert fen.pieces == []


@pytest.mark.parametrize(
    ("position", "player"),
    [
        ("W:W1:B2", Player.WHITE),
        ("B:W1:B2", Player.BLACK),
        ("w:W1:B2", Player.WHITE),
        ("b:W1:B2", Player.BLACK),
    ],
)
def test_parse_sets_player_to_move(position, player):
    fen = Fen()

    fen.parse(position)

    assert fen.player_to_move == player


def test_parse_reads_men():
    fen = Fen()

    fen.parse("W:W1,2:B31,32")

    assert [(p.owner, p.rank, p.square_ndx) for p in fen.pieces] == [
        (Player.WHITE, Rank.MAN, 1),
        (Player.WHITE, Rank.MAN, 2),
        (Player.BLACK, Rank.MAN, 31),
        (Player.BLACK, Rank.MAN, 32),
    ]


def test_parse_reads_kings_case_insensitive():
    fen = Fen()

    fen.parse("W:WK1,2:Bk31,K32")

    assert [(p.owner, p.rank, p.square_ndx) for p in fen.pieces] == [
        (Player.WHITE, Rank.KING, 1),
        (Player.WHITE, Rank.MAN, 2),
        (Player.BLACK, Rank.KING, 31),
        (Player.BLACK, Rank.KING, 32),
    ]


def test_parse_ignores_trailing_dot():
    fen = Fen()

    fen.parse("W:W1,2.:B3.")

    assert [(p.owner, p.rank, p.square_ndx) for p in fen.pieces] == [
        (Player.WHITE, Rank.MAN, 1),
        (Player.WHITE, Rank.MAN, 2),
        (Player.BLACK, Rank.MAN, 3),
    ]


def test_parse_empty_sections_produce_no_pieces():
    fen = Fen()

    fen.parse("W:W:B")

    assert fen.pieces == []


def test_parse_section_owner_letter_is_case_insensitive():
    fen = Fen()

    fen.parse("W:w1:b2")

    assert [(p.owner, p.rank, p.square_ndx) for p in fen.pieces] == [
        (Player.WHITE, Rank.MAN, 1),
        (Player.BLACK, Rank.MAN, 2),
    ]


def test_parse_replaces_previous_pieces():
    fen = Fen()
    fen.parse("W:W1,2:B31,32")

    fen.parse("B:W3:B4")

    assert [(p.owner, p.rank, p.square_ndx) for p in fen.pieces] == [
        (Player.WHITE, Rank.MAN, 3),
        (Player.BLACK, Rank.MAN, 4),
    ]


def test_parse_clears_the_same_pieces_list():
    fen = Fen()
    pieces = fen.pieces

    fen.parse("W:W1:B2")

    assert fen.pieces is pieces
    assert len(pieces) == 2


@pytest.mark.parametrize(
    "position",
    [
        "W:Wx:B",
        "W:W1:BK",
        "W:WKx:B",
    ],
)
def test_parse_raises_value_error_for_invalid_square_number(position):
    fen = Fen()

    with pytest.raises(ValueError):
        fen.parse(position)
