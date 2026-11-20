from pythia.core.move import Move
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator


class KingCapture(BaseMoveGenerator):
    """Генератор ударных ходов дамки.

    Правила взятия дамкой в русских и международных шашках совпадают:
    дамка перепрыгивает фигуру противника по диагонали и встаёт на любое
    свободное поле за ней, после чего обязана продолжить взятие, если это
    возможно. Взятая фигура до завершения хода остаётся на доске и
    помечается состоянием ``TAKEN``: через неё нельзя перепрыгнуть
    повторно и на неё нельзя встать.

    Генератор одинаково подходит и для белой, и для чёрной дамки:
    состояние фигуры (белая или чёрная дамка) однозначно определяется
    клеткой доски и отдельного указания цвета не требует.
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

    def generate_moves(self, board: DamBoard, square_ndx: int) -> list[Move]:
        """Возвращает ударные ходы дамки с клетки ``square_ndx``.

        Args:
            board: Текущая доска.
            square_ndx: Внутренний индекс клетки с дамкой.

        Returns:
            Список ходов, каждый из которых описывает законченную цепочку
            взятий. Ход завершается только тогда, когда продолжение взятия
            невозможно. Снятые фигуры перечислены в поле ``taken`` в
            порядке взятия.
        """

        # Рабочая копия состояний клеток: в ней взятые фигуры помечаются
        # как TAKEN, не изменяя исходную доску.
        states = [board.state(ndx) for ndx in range(self._size)]
        king_state = states[square_ndx]
        # Дамка покинула исходную клетку, поэтому в рабочей копии доски
        # эта клетка становится пустой.
        states[square_ndx] = SquareState.EMPTY

        moves: list[Move] = []
        self._search(
            states,
            from_ndx=square_ndx,
            current_ndx=square_ndx,
            king_state=king_state,
            taken=[],
            moves=moves,
        )
        return moves

    def continue_capture(
        self,
        states: list[SquareState],
        from_ndx: int,
        current_ndx: int,
        king_state: SquareState,
        taken: list[tuple[int, SquareState]],
        moves: list[Move],
        before_state: SquareState,
        after_state: SquareState,
    ) -> None:
        """Продолжает уже начатую цепочку взятий по правилам дамки.

        Метод используется, когда простая шашка превратилась в дамку
        прямо в процессе боя (правила русских шашек). Генератору передаётся
        рабочая копия доски ``states``, в которой уже помечены снятые фигуры
        и очищена исходная клетка, текущее положение ``current_ndx`` и
        накопленный список взятий ``taken``. Дальнейший перебор полностью
        совпадает с перебором для настоящей дамки.

        Args:
            states: Рабочая копия состояний клеток.
            from_ndx: Клетка, с которой начался ход (для поля ``Move``).
            current_ndx: Текущее положение превратившейся дамки.
            king_state: Состояние дамки (``WHITE_KING`` или ``BLACK_KING``).
            taken: Уже снятые фигуры в порядке взятия.
            moves: Список, в который добавляются завершённые ходы.
            before_state: Состояние фигуры в начале хода (простая шашка).
            after_state: Состояние фигуры в конце хода (дамка).
        """

        self._search(
            states,
            from_ndx=from_ndx,
            current_ndx=current_ndx,
            king_state=king_state,
            taken=taken,
            moves=moves,
            before_state=before_state,
            after_state=after_state,
        )

    def _search(
        self,
        states: list[SquareState],
        from_ndx: int,
        current_ndx: int,
        king_state: SquareState,
        taken: list[tuple[int, SquareState]],
        moves: list[Move],
        before_state: SquareState | None = None,
        after_state: SquareState | None = None,
    ) -> None:
        """Рекурсивно перебирает все продолжения цепочки взятий.

        ``before_state`` и ``after_state`` задают состояния хода. Для
        обычной дамки они совпадают с ``king_state``; при продолжении боя
        превратившейся простой шашкой начало хода остаётся простой, а
        конец — дамкой.
        """

        if before_state is None:
            before_state = king_state
        if after_state is None:
            after_state = king_state

        captures = self._captures_from(states, current_ndx, king_state)
        if not captures:
            # Продолжить взятие невозможно — цепочка закончена.
            if taken:
                moves.append(
                    Move(
                        from_square=from_ndx,
                        to_square=current_ndx,
                        before_state=before_state,
                        after_state=after_state,
                        taken=list(taken),
                    )
                )
            return

        for captured_ndx, landing_ndx in captures:
            captured_state = states[captured_ndx]
            # Взятая фигура остаётся на доске до конца хода, но не может
            # быть взята повторно и не пропускает через себя дамку.
            states[captured_ndx] = SquareState.TAKEN
            taken.append((captured_ndx, captured_state))
            self._search(
                states,
                from_ndx,
                landing_ndx,
                king_state,
                taken,
                moves,
                before_state,
                after_state,
            )
            taken.pop()
            states[captured_ndx] = captured_state

    def _captures_from(
        self,
        states: list[SquareState],
        square_ndx: int,
        king_state: SquareState,
    ) -> list[tuple[int, int]]:
        """Возвращает пары (индекс взятой фигуры, индекс приземления).

        Для каждой диагонали находится ближайшая фигура. Если она
        принадлежит противнику, то все свободные клетки за ней являются
        допустимыми точками приземления.
        """

        captures: list[tuple[int, int]] = []
        for direction in self._directions:
            target_ndx = square_ndx + direction
            # Свободные клетки проходятся насквозь, а рамка доски и любая
            # занятая клетка (своя фигура или TAKEN) останавливают поиск.
            while states[target_ndx].is_empty:
                target_ndx += direction

            if not self._is_opponent(states[target_ndx], king_state):
                continue

            landing_ndx = target_ndx + direction
            # Дамка может встать на любое свободное поле за взятой фигурой.
            while states[landing_ndx].is_empty:
                captures.append((target_ndx, landing_ndx))
                landing_ndx += direction
        return captures

    @staticmethod
    def _is_opponent(state: SquareState, king_state: SquareState) -> bool:
        """``True``, если ``state`` — фигура противника для данной дамки."""

        if king_state is SquareState.WHITE_KING:
            return state in (SquareState.BLACK_MAN, SquareState.BLACK_KING)
        if king_state is SquareState.BLACK_KING:
            return state in (SquareState.WHITE_MAN, SquareState.WHITE_KING)
        return False
