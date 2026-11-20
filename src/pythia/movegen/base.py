from typing import Protocol

from pythia.core.move import Move
from pythia.core.player import Player
from pythia.damboard.damboard import DamBoard


class BaseMoveGenerator(Protocol):
    """Base class for move generators."""

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Generate all legal moves for the given board."""
        raise NotImplementedError


class GenerateMoveList(Protocol):
    """Base class for move list generators."""

    def __init__(self, board: DamBoard, player: Player) -> None:
        """Binds the generator to a board and the player to move."""
        ...

    def generate_move_list(self) -> list[Move]:
        """Generate all legal moves for the given board."""
        raise NotImplementedError
