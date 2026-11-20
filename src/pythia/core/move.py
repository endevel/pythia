from dataclasses import dataclass, field

from pythia.core.square_state import SquareState


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
