from typing import Protocol

from pythia.damboard.damboard import DamBoard


class Evaluation(Protocol):
    
    def evaluate(self, board: DamBoard) -> int:
        ...
