from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator


class InternationalManCapture(BaseMoveGenerator):
    """Генератор ударных ходов простой шашки по правилам международных шашек.

    Простая шашка бьёт на одну клетку вперёд и назад: она перепрыгивает
    стоящую рядом по диагонали фигуру противника и встаёт на свободное
    поле сразу за ней. Взятие обязательно продолжается, пока это возможно.

    Превращение в дамку происходит только в конце цепочки взятий и только
    тогда, когда последняя клетка хода находится на дамочном ряду. Если
    простая достигает дамочного ряда, но может продолжать взятие, она
    обязана продолжить его как простая — превращения при этом не
    происходит. Если же продолжать взятие нельзя, шашка остаётся на
    дамочном поле и превращается в дамку, а цепочка на этом заканчивается.

    Генератор одинаково подходит и для белой, и для чёрной простой шашки:
    цвет фигуры однозначно определяется клеткой доски, а дамочный ряд
    выбирается по цвету.
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
        # Ширина строки плоского массива с учётом рамки.
        self._stride = board.width + 2
        # Полный размер плоского массива вместе с рамкой.
        self._size = (board.height + 2) * self._stride
        # Дамочный ряд зависит от цвета простой шашки: белая движется в
        # сторону уменьшения индекса и превращается на первом ряду, чёрная
        # движется в сторону увеличения индекса и превращается на последнем.
        self._white_promotion_row = 1
        self._black_promotion_row = board.height

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Возвращает ударные ходы простой шашки с клетки ``square_ndx``.

        Args:
            board: Текущая доска.
            square_ndx: Внутренний индекс клетки с простой шашкой.

        Returns:
            Список ходов, каждый из которых описывает законченную цепочку
            взятий. Ход завершается только тогда, когда продолжение взятия
            невозможно. Снятые фигуры перечислены в поле ``taken`` в
            порядке взятия.
        """

        # Рабочая копия состояний клеток: в ней взятые фигуры помечаются
        # как TAKEN, не изменяя исходную доску.
        states = [board.state(ndx) for ndx in range(self._size)]
        man_state = states[square_ndx]
        # Шашка покинула исходную клетку, поэтому в рабочей копии доски
        # эта клетка становится пустой.
        states[square_ndx] = SquareState.EMPTY

        promotion_row = (
            self._white_promotion_row
            if man_state is SquareState.WHITE_MAN
            else self._black_promotion_row
        )

        moves: list[Move] = []
        self._search(
            states,
            from_ndx=square_ndx,
            current_ndx=square_ndx,
            man_state=man_state,
            promotion_row=promotion_row,
            taken=[],
            path=[square_ndx],
            moves=moves,
        )
        return moves

    def _search(
        self,
        states: list[SquareState],
        from_ndx: int,
        current_ndx: int,
        man_state: SquareState,
        promotion_row: int,
        taken: list[tuple[int, SquareState]],
        path: list[int],
        moves: list[Move],
    ) -> None:
        """Рекурсивно перебирает все продолжения цепочки взятий."""

        captures = self._captures_from(states, current_ndx, man_state)
        if not captures:
            # Продолжить взятие невозможно — цепочка закончена.
            if taken:
                after_state = man_state
                # Превращение фиксируется только по последней клетке хода.
                if current_ndx // self._stride == promotion_row:
                    after_state = man_state.promote()
                moves.append(
                    Move(
                        from_square=from_ndx,
                        to_square=current_ndx,
                        before_state=man_state,
                        after_state=after_state,
                        taken=list(taken),
                        path=tuple(path),
                    )
                )
            return

        for captured_ndx, landing_ndx in captures:
            captured_state = states[captured_ndx]
            # Взятая фигура остаётся на доске до конца хода, но не может
            # быть взята повторно и не пропускает через себя шашку.
            states[captured_ndx] = SquareState.TAKEN
            taken.append((captured_ndx, captured_state))
            path.append(landing_ndx)
            # Простая шашка всегда продолжает бой как простая, даже если
            # текущая клетка находится на дамочном ряду.
            self._search(
                states,
                from_ndx,
                landing_ndx,
                man_state,
                promotion_row,
                taken,
                path,
                moves,
            )
            path.pop()
            taken.pop()
            states[captured_ndx] = captured_state

    def _captures_from(
        self,
        states: list[SquareState],
        square_ndx: int,
        man_state: SquareState,
    ) -> list[tuple[int, int]]:
        """Возвращает пары (индекс взятой фигуры, индекс приземления).

        Простая шашка бьёт только на одну клетку: фигура противника должна
        стоять непосредственно рядом по диагонали, а клетка сразу за ней
        должна быть свободной.
        """

        captures: list[tuple[int, int]] = []
        for direction in self._directions:
            captured_ndx = square_ndx + direction
            if not self._is_opponent(states[captured_ndx], man_state):
                continue
            landing_ndx = captured_ndx + direction
            if states[landing_ndx].is_empty:
                captures.append((captured_ndx, landing_ndx))
        return captures

    @staticmethod
    def _is_opponent(state: SquareState, man_state: SquareState) -> bool:
        """``True``, если ``state`` — фигура противника для данной шашки."""

        if man_state is SquareState.WHITE_MAN:
            return state in (SquareState.BLACK_MAN, SquareState.BLACK_KING)
        if man_state is SquareState.BLACK_MAN:
            return state in (SquareState.WHITE_MAN, SquareState.WHITE_KING)
        return False
