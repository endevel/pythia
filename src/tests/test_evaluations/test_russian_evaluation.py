from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.russian_evaluation import RussianEvaluation


RUSSIAN_START_FEN = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"
def test_initial_state():
    board = DamBoard()
    board.setup(RUSSIAN_START_FEN)
    eval = RussianEvaluation()
    score = eval.evaluate(board)
    assert score == 0
    
