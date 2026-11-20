from __future__ import annotations

from enum import Enum


class SquareState(Enum):
    """Состояние клетки игрового поля."""

    EMPTY = 0
    WHITE_MAN = 1
    WHITE_KING = 2
    BLACK_MAN = 3
    BLACK_KING = 4
    TAKEN = 5
    OUT_OF_BOARD = 6

    def promote(self) -> SquareState:
        """Возвращает состояние клетки после превращения простой шашки в дамку.

        Для простых шашек возвращается соответствующая дамка, для всех
        остальных состояний (дамки, пустая клетка, снятая фигура, клетка
        вне доски) возвращается исходное состояние.
        """
        if self is SquareState.WHITE_MAN:
            return SquareState.WHITE_KING
        if self is SquareState.BLACK_MAN:
            return SquareState.BLACK_KING
        return self

    @property
    def is_empty(self) -> bool:
        """``True``, если клетка пустая и на ней нет фигуры."""
        return self is SquareState.EMPTY
