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
