"""Тесты полей превращения простой в дамку — п.4 movegen.md."""

from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.rules import INTERNATIONAL, RUSSIAN


def _numbers(generator: MoveGenerator, player: Player) -> set[int]:
    """Поля превращения игрока в номерах игровых полей (1..N)."""
    return {generator._board.number_at(ndx) for ndx in generator.promotion_squares(player)}


def test_standard_white_promotes_on_top_row():
    generator = MoveGenerator(Damboard(BoardSize.STANDARD), RUSSIAN)
    # Белые стоят снизу, дамочные поля — верхняя горизонталь: клетки 1-4.
    assert _numbers(generator, Player.WHITE) == {1, 2, 3, 4}


def test_standard_black_promotes_on_bottom_row():
    generator = MoveGenerator(Damboard(BoardSize.STANDARD), RUSSIAN)
    # Чёрные стоят сверху, дамочные поля — нижняя горизонталь: клетки 29-32.
    assert _numbers(generator, Player.BLACK) == {29, 30, 31, 32}


def test_big_white_promotes_on_top_row():
    generator = MoveGenerator(Damboard(BoardSize.BIG), INTERNATIONAL)
    # Международные 10x10: дамочные поля белых — клетки 1-5.
    assert _numbers(generator, Player.WHITE) == {1, 2, 3, 4, 5}


def test_big_black_promotes_on_bottom_row():
    generator = MoveGenerator(Damboard(BoardSize.BIG), INTERNATIONAL)
    # Международные 10x10: дамочные поля чёрных — клетки 46-50.
    assert _numbers(generator, Player.BLACK) == {46, 47, 48, 49, 50}


def test_promotion_squares_are_dark_squares_only():
    board = Damboard(BoardSize.STANDARD)
    generator = MoveGenerator(board, RUSSIAN)
    # Все поля превращения — тёмные игровые клетки, видимые доске.
    for player in (Player.WHITE, Player.BLACK):
        for ndx in generator.promotion_squares(player):
            assert board.state(ndx) != SquareState.OUT_OF_BOARD
