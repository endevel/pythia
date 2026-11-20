from typing import Protocol

from pythia.core.move import Move
from pythia.damboard.damboard import DamBoard


class BaseMoveGenerator(Protocol):
    """Base class for move generators."""

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Generate all legal moves for the given board."""
        raise NotImplementedError
