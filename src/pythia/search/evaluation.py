"""Оценка позиции — начальный этап: только материал (п.2 search.md).

Оценка сознательно выделена за интерфейс `Evaluator`: в дальнейшем она
будет расширяться (позиционные бонусы, подвижность, темп, эндшпильные
критерии и т.д.), а поиску достаточно подменить реализацию.
"""

from collections.abc import Mapping
from typing import Protocol

from pythia.core.player import Player
from pythia.core.square_state import SquareState


class Evaluator(Protocol):
    """Интерфейс оценки позиции.

    Оценка возвращает счёт с точки зрения стороны `player`: большее
    значение — лучше для `player`.
    """

    def evaluate(self, states: Mapping[int, SquareState], player: Player) -> int:
        """Оценка позиции по таблице состояний клеток."""
        ...


class MaterialEvaluator:
    """Материальная оценка: простая — 100 очков, дамка — 270 очков (п.2).

    Считается разность материала белых и чёрных (белым — плюс), затем
    знак приводится к точке зрения играющей стороны: негмакс в поиске
    ожидает счёт для стороны, чей ход.
    """

    MAN_VALUE = 100
    KING_VALUE = 270

    # Веса состояний клеток со знаком: белые — плюс, чёрные — минус.
    _WEIGHTS: dict[SquareState, int] = {
        SquareState.WHITE_MAN: MAN_VALUE,
        SquareState.WHITE_KING: KING_VALUE,
        SquareState.BLACK_MAN: -MAN_VALUE,
        SquareState.BLACK_KING: -KING_VALUE,
    }

    def evaluate(self, states: Mapping[int, SquareState], player: Player) -> int:
        """Материальный баланс позиции с точки зрения `player`."""
        score = sum(self._WEIGHTS.get(state, 0) for state in states.values())
        return score if player == Player.WHITE else -score
