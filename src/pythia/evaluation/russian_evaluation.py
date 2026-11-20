from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.evaluation import Evaluation


class RussianEvaluation(Evaluation):
    """Оценка позиции для русских шашек.

    Класс хранит веса фигур и шаблоны «колов» — характерных для русских
    шашек построений, которые учитываются при оценке позиции.

    Attributes:
        _man_weight: Стоимость простой шашки.
        _king_weight: Стоимость дамки.
        _white_kol: Пара множеств с номерами полей (1..N), образующих
            белый «кол»: (поле дамки, поля простых шашек).
    """

    def __init__(self):
        self._man_weight = 100
        self._king_weight = 270
        self._white_kol: tuple[set[int], set[int]] = ({14}, {5, 13})
        self._black_kol: tuple[set[int], set[int]] = ({20, 28}, {19})
        self._kol_weight: int = 10
        self._white_center: set[int] = {18, 19, 22, 23}
        self._black_center: set[int] = {10, 11, 14, 15}
        self._center_weight: int = 10

    def evaluate(self, board: DamBoard) -> int:
        """Возвращает материальную оценку позиции в пользу белых.

        Положительное значение означает перевес белых, отрицательное —
        чёрных. Оценка считается как разность стоимостей белых и чёрных
        фигур.

        Args:
            board: Доска, позиция которой оценивается.

        Returns:
            Материальный перевес белых в единицах веса простой шашки.
        """

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

        white_center_score = board.white_pieces.intersection(self._white_center)
        black_center_score = board.black_pieces.intersection(self._black_center)
        score += len(white_center_score) * self._center_weight
        score -= len(black_center_score) * self._center_weight

        return score
