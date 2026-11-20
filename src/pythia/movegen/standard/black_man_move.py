from pythia.core.move import Move
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator


class BlackManMove(BaseMoveGenerator):
    """Генератор тихих ходов чёрной простой шашки.

    Чёрная простая шашка ходит только вперёд — в сторону увеличения
    внутреннего индекса плоского массива.
    """

    def __init__(self, board: DamBoard):
        super().__init__()
        # Доска хранится плоским массивом с рамкой толщиной в одну клетку,
        # поэтому вертикальный шаг между соседними клетками равен width + 2.
        # Ход вперёд-вправо смещает индекс на +(width + 3),
        # ход вперёд-влево — на +(width + 1).
        self._move_right = board.width + 3
        self._move_left = board.width + 1
        # Ширина строки плоского массива с учётом рамки.
        self._stride = board.width + 2
        # Чёрная простая шашка идёт в сторону увеличения индекса,
        # поэтому дамочным для неё является последний ряд (индекс ряда height).
        self._promotion_row = board.height

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Возвращает тихие ходы чёрной простой шашки с клетки ``square_ndx``.

        Args:
            board: Текущая доска.
            square_ndx: Внутренний индекс клетки с чёрной простой шашкой.

        Returns:
            Список ходов на свободные клетки по обеим передним диагоналям.
        """

        piece_state = board[square_ndx]
        moves = []
        for offset in (self._move_right, self._move_left):
            next_ndx = square_ndx + offset
            if board[next_ndx].is_empty:
                # Простая шашка, дошедшая до дамочного ряда, превращается
                # в дамку — это фиксируется в состоянии после хода.
                after_state = piece_state
                if next_ndx // self._stride == self._promotion_row:
                    after_state = piece_state.promote()
                moves.append(
                    Move(
                        from_square=square_ndx,
                        to_square=next_ndx,
                        before_state=piece_state,
                        after_state=after_state,
                    )
                )
        return moves
