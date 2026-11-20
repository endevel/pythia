import pytest

from pythia.core.board_size import BoardSize
from pythia.core.player import Player
from pythia.movegen.international_move_gen import InternationalMoveGen
from pythia.movegen.perft import (
    INTERNATIONAL_START_FEN,
    RUSSIAN_START_FEN,
    board_from_fen,
    perft,
    perft_divide,
)
from pythia.movegen.russian_move_gen import RussianMoveGen

# Эталонные значения perft из независимых движков (Scan, Flux, pydraughts).
# Любое расхождение означает ошибку в генерации ходов или в откате хода.
RUSSIAN_REFERENCE = {
    1: 7,
    2: 49,
    3: 302,
    4: 1469,
    5: 7482,
    6: 37986,
}

INTERNATIONAL_REFERENCE = {
    1: 9,
    2: 81,
    3: 658,
    4: 4265,
    5: 27117,
    6: 167140,
}


@pytest.fixture
def russian_board():
    return board_from_fen(RUSSIAN_START_FEN)


@pytest.fixture
def international_board():
    return board_from_fen(INTERNATIONAL_START_FEN, BoardSize.BIG)


@pytest.mark.parametrize(
    ("depth", "expected"), sorted(RUSSIAN_REFERENCE.items())
)
def test_russian_perft(russian_board, depth, expected):
    assert (
        perft(russian_board, Player.WHITE, depth, RussianMoveGen) == expected
    )


@pytest.mark.parametrize(
    ("depth", "expected"), sorted(INTERNATIONAL_REFERENCE.items())
)
def test_international_perft(international_board, depth, expected):
    assert (
        perft(international_board, Player.WHITE, depth, InternationalMoveGen)
        == expected
    )


def test_perft_zero_depth_is_one(russian_board):
    assert perft(russian_board, Player.WHITE, 0, RussianMoveGen) == 1


def test_perft_negative_depth_is_rejected(russian_board):
    with pytest.raises(ValueError):
        perft(russian_board, Player.WHITE, -1, RussianMoveGen)


def test_perft_accepts_generator_instance(russian_board):
    generator = RussianMoveGen(russian_board, Player.WHITE)

    assert perft(russian_board, Player.WHITE, 3, generator) == 302


def test_perft_restores_board(russian_board):
    fen_before = russian_board.to_fen(Player.WHITE)

    perft(russian_board, Player.WHITE, 4, RussianMoveGen)

    assert russian_board.to_fen(Player.WHITE) == fen_before
    assert russian_board.player_to_move == Player.WHITE


def test_perft_restores_board_international(international_board):
    fen_before = international_board.to_fen(Player.WHITE)

    perft(international_board, Player.WHITE, 3, InternationalMoveGen)

    assert international_board.to_fen(Player.WHITE) == fen_before
    assert international_board.player_to_move == Player.WHITE


@pytest.mark.parametrize("depth", [1, 2])
def test_russian_perft_divide_sums_to_perft(russian_board, depth):
    divide = perft_divide(russian_board, Player.WHITE, depth, RussianMoveGen)

    assert sum(nodes for _, nodes in divide) == perft(
        russian_board, Player.WHITE, depth, RussianMoveGen
    )
    assert len(divide) == RUSSIAN_REFERENCE[1]


@pytest.mark.parametrize("depth", [1, 2])
def test_international_perft_divide_sums_to_perft(
    international_board, depth
):
    divide = perft_divide(
        international_board, Player.WHITE, depth, InternationalMoveGen
    )

    assert sum(nodes for _, nodes in divide) == perft(
        international_board, Player.WHITE, depth, InternationalMoveGen
    )
    assert len(divide) == INTERNATIONAL_REFERENCE[1]


def test_perft_divide_requires_positive_depth(russian_board):
    with pytest.raises(ValueError):
        perft_divide(russian_board, Player.WHITE, 0, RussianMoveGen)
