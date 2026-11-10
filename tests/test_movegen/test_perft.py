"""Perft-валидация генератора ходов — см. pythia.movegen.perft.

Эталонные значения для стартовой позиции международных шашек (10x10,
20+20 шашек) опубликованы и совпадают у независимых движков (Scan, Flux):

    perft(1) = 9        perft(5) = 27 117
    perft(2) = 81       perft(6) = 167 140
    perft(3) = 658      perft(7) = 1 049 442
    perft(4) = 4 265    perft(8) = 6 483 961

Perft использует make_move/unmake_move, поэтому тест заодно проверяет
корректность отката хода: любое повреждение позиции искажает числа.
Глубины 1–5 быстрые (<0.5 c); глубина 6 — около секунды, глубина 7 —
около 6 c, поэтому они помечены как медленные.
"""

from collections.abc import Iterable

import pytest

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.movegen.move import Move
from pythia.movegen.perft import generator_from_fen, perft, perft_divide
from pythia.movegen.rules import INTERNATIONAL

START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20."
)

PERFT_START_VALUES = {
    1: 9,
    2: 81,
    3: 658,
    4: 4_265,
    5: 27_117,
}


@pytest.mark.parametrize(("depth", "expected"), sorted(PERFT_START_VALUES.items()))
def test_perft_start_position(depth: int, expected: int):
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    assert perft(generator, Player.WHITE, depth) == expected


@pytest.mark.slow
def test_perft_start_position_depth_6():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    assert perft(generator, Player.WHITE, 6) == 167_140


@pytest.mark.slow
def test_perft_start_position_depth_7():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    assert perft(generator, Player.WHITE, 7) == 1_049_442


def test_perft_divide_sums_to_perft():
    # divide по корневым ходам должен сходиться с полным perft:
    # стартовая позиция, глубина 3.
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    divide = perft_divide(generator, Player.WHITE, 3)
    assert sum(divide.values()) == 658
    # 9 корневых ходов стартовой позиции.
    assert len(divide) == 9


def test_perft_divide_root_moves_of_start_position():
    # Корневые ходы стартовой позиции: 9 тихих ходов простых 31–35.
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    divide = perft_divide(generator, Player.WHITE, 1)
    expected = {
        (31, 26): 1,
        (31, 27): 1,
        (32, 27): 1,
        (32, 28): 1,
        (33, 28): 1,
        (33, 29): 1,
        (34, 29): 1,
        (34, 30): 1,
        (35, 30): 1,
    }
    assert {move.path: count for move, count in divide.items()} == expected


def test_perft_position_with_capture_landing_on_vacated_square():
    # Позиция после 1.31-26 17-21 2.26x21(->17): поле 21 освободилось,
    # и обе чёрные простые, стоящие на диагоналях белой 17, обязаны
    # бить её: 11x17->22 и 12x17->21 (приземление на освободившееся
    # поле 21). Регрессия к ошибке «побитые в завершённом ходе
    # остаются TAKEN», из-за которой взятие 12x21 не генерировалось.
    generator = generator_from_fen(
        "B:W17,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
        "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,18,19,20.",
        INTERNATIONAL,
        BoardSize.BIG,
    )
    moves = generator.generate(Player.BLACK)
    assert _paths(moves) == {((11, 22), (17,)), ((12, 21), (17,))}


def _paths(moves: Iterable[Move]) -> set[tuple[tuple[int, ...], tuple[int, ...]]]:
    """Ходы в виде {(path, captured)} — для сравнения множеств."""
    return {(move.path, move.captured) for move in moves}
