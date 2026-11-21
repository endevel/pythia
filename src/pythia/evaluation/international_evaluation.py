from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.evaluation import Evaluation


class InternationalEvaluation(Evaluation):
    def __init__(self):
        self._man_weight = 100
        self._king_weight = 270

    def evaluate(self, board: DamBoard) -> int:
        score = 0
        for ndx in board:
            state = board.state(ndx)
            if state is SquareState.WHITE_MAN:
                score += self._man_weight
            elif state is SquareState.WHITE_KING:
                score += self._king_weight
            elif state is SquareState.BLACK_MAN:
                score -= self._man_weight
            elif state is SquareState.BLACK_KING:
                score -= self._king_weight
        return score
