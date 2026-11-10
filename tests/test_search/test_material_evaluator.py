"""Тесты материальной оценки — `MaterialEvaluator` (п.2 search.md)."""

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.rules import RUSSIAN
from pythia.search.evaluation import MaterialEvaluator


def _score(fen: str) -> int:
    """Оценка позиции с точки зрения белых."""
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    states = MoveGenerator(board, RUSSIAN).states
    return MaterialEvaluator().evaluate(states, Player.WHITE)


def _score_for(states: dict, player: Player) -> int:
    return MaterialEvaluator().evaluate(states, player)


def test_initial_position_is_balanced():
    # Начальная расстановка: по 12 простых у каждой стороны — счёт 0.
    fen = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12."
    assert _score(fen) == 0


def test_extra_man_is_worth_100():
    # Лишняя простая у белых: белым +100, чёрным -100.
    fen = "W:W23,24:B18."
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    states = MoveGenerator(board, RUSSIAN).states
    assert _score_for(states, Player.WHITE) == 100
    assert _score_for(states, Player.BLACK) == -100


def test_king_outweighs_man():
    # Дамка (270) против простой (100): перевес белых 170 очков.
    fen = "W:WK1:B18."
    assert _score(fen) == 170


def test_equal_kings_and_men_is_zero():
    # Дамка и простая против дамки и простой — счёт 0.
    fen = "W:WK1,24:BK30,19."
    assert _score(fen) == 0


def test_empty_board_is_zero():
    # Пустая доска (без setup) — материала нет, счёт 0 для обеих сторон.
    # (FEN-парсер не принимает позицию вообще без секций фигур.)
    board = Damboard(BoardSize.STANDARD)
    states = MoveGenerator(board, RUSSIAN).states
    evaluator = MaterialEvaluator()
    assert evaluator.evaluate(states, Player.WHITE) == 0
    assert evaluator.evaluate(states, Player.BLACK) == 0
