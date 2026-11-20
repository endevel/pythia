from pythia.core.move import Move
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator


class KingMove(BaseMoveGenerator):
    """Генератор тихих ходов дамки.

    Дамка ходит по диагонали на любое число свободных клеток в любую
    сторону, поэтому генератор одинаково подходит и для белой, и для
    чёрной дамки. Состояние фигуры (белая или чёрная дамка) однозначно
    определяется клеткой доски и отдельного указания цвета не требует.
    """

    def __init__(self, board: DamBoard):
        super().__init__()
        # Доска хранится плоским массивом с рамкой толщиной в одну клетку,
        # поэтому вертикальный шаг между соседними клетками равен width + 2.
        # Смещения на одну клетку по четырём диагоналям:
        # вверх-влево, вверх-вправо, вниз-влево, вниз-вправо.
        self._directions = (
            -(board.width + 3),
            -(board.width + 1),
            board.width + 1,
            board.width + 3,
        )

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Возвращает тихие ходы дамки с клетки ``square_ndx``.

        Args:
            board: Текущая доска.
            square_ndx: Внутренний индекс клетки с дамкой.

        Returns:
            Список ходов на все свободные клетки по четырём диагоналям.
            Движение по каждой диагонали прекращается перед первой
            занятой клеткой.
        """

        piece_state = board[square_ndx]
        moves = []
        for direction in self._directions:
            next_ndx = square_ndx + direction
            while board[next_ndx].is_empty:
                moves.append(
                    Move(
                        from_square=square_ndx,
                        to_square=next_ndx,
                        before_state=piece_state,
                        after_state=piece_state,
                        path=(square_ndx, next_ndx),
                    )
                )
                next_ndx += direction
        return moves
