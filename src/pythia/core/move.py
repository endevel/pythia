from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from pythia.core.square_state import SquareState

if TYPE_CHECKING:
    from pythia.damboard.damboard import DamBoard


@dataclass
class Move:
    """Represents a move in the game."""

    from_square: int
    to_square: int
    before_state: SquareState
    after_state: SquareState
    # List of (square index, square state) for taken pieces.
    # default_factory creates a new list for every instance, so instances
    # never share the same mutable default object.
    taken: list[tuple[int, SquareState]] = field(default_factory=list)
    # Последовательность внутренних индексов клеток хода: начальная клетка,
    # промежуточные приземления при взятии и конечная клетка. Для тихого
    # хода содержит ровно две клетки. Поле не участвует в сравнении ходов,
    # чтобы не менять существующую семантику равенства Move.
    path: tuple[int, ...] = field(default_factory=tuple, compare=False)


def move_to_str(move: Move, board: DamBoard) -> str:
    """Возвращает ход в «человеческом» формате нотации шашек.

    Тихий ход печатается через дефис (``32-28``), взятие — через ``x``
    (``31x22x13``). Для взятия используется полный путь ``move.path`` с
    промежуточными полями приземления; если путь не задан или не
    согласуется с начальным и конечным полями, печатаются только они.

    Args:
        move: Ход с внутренними индексами клеток плоского массива.
        board: Доска, используемая для перевода внутренних индексов
            в номера игровых полей (1..N).

    Returns:
        Строка хода в нотации с номерами полей, например ``32-28``
        или ``31x22x13``.
    """

    separator = "x" if move.taken else "-"
    path = move.path
    if len(path) < 2 or path[0] != move.from_square or path[-1] != move.to_square:
        path = (move.from_square, move.to_square)
    return separator.join(str(board.number_at(ndx)) for ndx in path)
