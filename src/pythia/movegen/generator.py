"""Каркас генератора ходов `MoveGenerator(Damboard, Rules)` — пп. 3–4 movegen.md.

`Damboard` остаётся неизменяемым источником истины: рабочая позиция
генератора живёт в собственной копии состояний `self._states`.
"""

from collections.abc import Iterable

from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import Damboard
from pythia.movegen.move import Move
from pythia.movegen.rules import Rules


class MoveGenerator:
    """Генератор ходов: геометрия — от `Damboard`, вариативность — в `Rules`."""

    def __init__(self, board: Damboard, rules: Rules):
        self._board = board
        self._rules = rules
        self._stride = board.width + 2
        self._move_left = self._stride + 1
        self._move_right = self._stride - 1
        # Все четыре диагонали: дамка бьёт в любом направлении (п.4 movegen.md).
        self._diagonals = (
            -self._move_left,
            -self._move_right,
            self._move_left,
            self._move_right,
        )
        # Отображение внутреннего индекса -> номер игрового поля (1..N).
        self._number_of = {ndx: board.number_at(ndx) for ndx in board}
        # Рабочая копия состояний игровых клеток; Damboard не мутируется (п.4).
        self._states = {ndx: board.state(ndx) for ndx in self._number_of}
        # Поля превращения простой в дамку (внутренние индексы), по игрокам.
        self._promotion_squares = self._build_promotion_squares()

    def generate(self, player: Player) -> list[Move]:
        """Все ходы игрока: взятия (обязательны), иначе тихие ходы.

        Алгоритм DFS по дереву взятий и генерация тихих ходов — п.4 movegen.md.
        """
        # Сначала ищем взятия (обязательны), при их отсутствии — тихие ходы.
        if player == Player.WHITE:
            return self._generate_all_white_moves()
        return self._generate_all_black_moves()

    def promotion_squares(self, player: Player) -> frozenset[int]:
        """Поля (внутренние индексы), где простая игрока становится дамкой.

        Вычисляются один раз в `__init__` из `Rules.promotion_rows` и
        геометрии доски; в рабочей позиции не меняются.
        """
        return self._promotion_squares[player]

    def _pieces_of(self, player: Player) -> list[int]:
        """Внутренние индексы всех фигур игрока."""
        if player == Player.WHITE:
            own = (SquareState.WHITE_MAN, SquareState.WHITE_KING)
        else:
            own = (SquareState.BLACK_MAN, SquareState.BLACK_KING)
        return [ndx for ndx, state in self._states.items() if state in own]

    def _build_promotion_squares(self) -> dict[Player, frozenset[int]]:
        """Строки превращения `Rules.promotion_rows` -> внутренние индексы.

        Смещение строки отсчитывается от самого дальнего от игрока ряда
        (0 — дамочный, 1 — предыдущий и т.д.). В геометрии
        `build_standard_board` белые стоят в нижних строках, поэтому их
        дамочная строка — верхняя игровая (row 1), а чёрных — нижняя
        (row height). Из строки берутся только тёмные игровые клетки.
        """
        height = self._board.height
        return {
            Player.WHITE: self._squares_in_rows(
                1 + offset for offset in self._rules.promotion_rows
            ),
            Player.BLACK: self._squares_in_rows(
                height - offset for offset in self._rules.promotion_rows
            ),
        }

    def _squares_in_rows(self, rows: Iterable[int]) -> frozenset[int]:
        """Тёмные игровые клетки (внутренние индексы) данных строк."""
        stride = self._stride
        squares: set[int] = set()
        for row in rows:
            for col in range(1, self._board.width + 1):
                ndx = row * stride + col
                # Светлые клетки и бортик не входят в `self._number_of`.
                if ndx in self._number_of:
                    squares.add(ndx)
        return frozenset(squares)

    def _generate_all_white_moves(self) -> list[Move]:
        """Все ходы белых: взятия (обязательны), иначе тихие ходы."""
        moves = self._generate_white_captures()
        if not moves:
            moves = self._generate_white_moves()
        return moves

    def _generate_all_black_moves(self) -> list[Move]:
        """Все ходы чёрных: взятия (обязательны), иначе тихие ходы."""
        moves = self._generate_black_captures()
        if not moves:
            moves = self._generate_black_moves()
        return moves

    def _generate_white_moves(self) -> list[Move]:
        """Все ходы белых фигур."""
        moves: list[Move] = []
        for ndx in self._pieces_of(Player.WHITE):
            # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
            if self._states[ndx] == SquareState.WHITE_MAN:
                moves.extend(self._generate_white_man_moves(ndx))
            elif self._states[ndx] == SquareState.WHITE_KING:
                moves.extend(self._generate_white_king_moves(ndx))
        return moves

    def _generate_white_captures(self) -> list[Move]:
        """Все взятия белых фигур."""
        moves: list[Move] = []
        for ndx in self._pieces_of(Player.WHITE):
            if self._states[ndx] == SquareState.WHITE_MAN:
                moves.extend(self._generate_white_man_captures(ndx))
            elif self._states[ndx] == SquareState.WHITE_KING:
                moves.extend(self._generate_white_king_captures(ndx))
        return moves

    def _generate_white_man_captures(self, ndx: int) -> list[Move]:
        """Все взятия белых простых фигур."""
        moves: list[Move] = []
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
        return moves

    def _generate_white_king_captures(self, ndx: int) -> list[Move]:
        """Все взятия белых дамок."""
        moves: list[Move] = []
        self._king_captures_from(
            ndx,
            [ndx],
            [],
            moves,
            own=(SquareState.WHITE_MAN, SquareState.WHITE_KING),
            king=SquareState.WHITE_KING,
        )
        return moves

    def _king_captures_from(
        self,
        ndx: int,
        path: list[int],
        captured: list[int],
        out: list[Move],
        own: tuple[SquareState, SquareState],
        king: SquareState,
    ) -> None:
        """DFS по дереву взятий дамки из `ndx` — общий для обоих цветов (п.4).

        `path` содержит внутренние индексы: исходное поле и все поля
        приземления, `captured` — внутренние индексы побитых фигур.
        По каждой из четырёх диагоналей `_scan_king` возвращает жертву и
        все поля приземления за ней; каждое приземление — точка ветвления
        DFS. Полная цепочка взятия фиксируется в `out`, когда ни одного
        продолжения найти не удалось.
        """
        extended = False
        for delta in self._diagonals:
            victim, landings = self._scan_king(ndx, delta, own)
            if victim is None:
                continue
            for landing in landings:
                extended = True
                saved_victim = self._states[victim]
                # Применяем шаг: жертва -> TAKEN, дамка -> landing.
                self._states[ndx] = SquareState.EMPTY
                self._states[victim] = SquareState.TAKEN
                self._states[landing] = king
                self._king_captures_from(
                    landing,
                    [*path, landing],
                    [*captured, victim],
                    out,
                    own,
                    king,
                )
                # Откат шага (жертва и посадка известны локально в кадре).
                self._states[landing] = SquareState.EMPTY
                self._states[victim] = saved_victim
                self._states[ndx] = king
        if captured and not extended:
            out.append(
                Move(
                    # `Move.path`/`Move.captured` хранят номера игровых полей
                    # (1..N), а не внутренние индексы (пп. 3–4 movegen.md).
                    path=tuple(self._number_of[s] for s in path),
                    captured=tuple(self._number_of[v] for v in captured),
                )
            )

    def _scan_king(
        self,
        ndx: int,
        delta: int,
        own: tuple[SquareState, SquareState],
    ) -> tuple[int | None, list[int]]:
        """Жертва и все поля приземления за ней по лучу `delta` (п.4 movegen.md).

        1. скольжение по лучу: `EMPTY` — пропускаем;
        2. `TAKEN` или своя фигура — взятия в направлении нет: битую шашку
           нельзя перепрыгивать вторично, свою перепрыгивать нельзя;
        3. чужая фигура — жертва; дальше собираем все пустые клетки сразу
           за ней до первого препятствия: дамка может остановиться на любом
           из них (общее правило для русских и международных шашек).
        """
        cur = ndx + delta
        while cur in self._states and self._states[cur] == SquareState.EMPTY:
            cur += delta
        if cur not in self._states or self._states[cur] in (SquareState.TAKEN, *own):
            return None, []
        victim = cur
        cur += delta
        landings: list[int] = []
        while cur in self._states and self._states[cur] == SquareState.EMPTY:
            landings.append(cur)
            cur += delta
        return victim, landings

    def _generate_white_man_moves(self, ndx: int) -> list[Move]:
        """Все тихие ходы белой простой: два соседних поля на `EMPTY`.

        Белые движутся в сторону уменьшения внутренних индексов (вверх
        по доске), поэтому оба соседних  поля получаются вычитанием
        `self._move_left` и `self._move_right`.
        """
        moves: list[Move] = []
        for delta in (-self._move_left, -self._move_right):
            next_ndx = ndx + delta
            # Клетки «бортика» не входят в `self._states` (см. `__init__`),
            # поэтому проверка `in` эквивалентна проверке `OUT_OF_BOARD`.
            if next_ndx in self._states and self._states[next_ndx] == SquareState.EMPTY:
                moves.append(
                    Move(
                        # `Move.path` хранит номера игровых полей (1..N),
                        # а не внутренние индексы (пп. 3–4 movegen.md).
                        path=(self._number_of[ndx], self._number_of[next_ndx]),
                        # Для тихого хода `captured` — пустой кортеж,
                        # а не `None`: `Move.captured: tuple[int, ...]`.
                        captured=(),
                        # Пешка, завершившая ход на строке превращения,
                        # получает `promotes=True` (п.4 movegen.md).
                        promotes=next_ndx in self._promotion_squares[Player.WHITE],
                    )
                )
        return moves

    def _generate_white_king_moves(self, ndx: int) -> list[Move]:
        """Все тихие ходы белой дамки: скольжение по всем четырём диагоналям.

        Дамка движется в любом направлении до первого препятствия,
        поэтому геометрия одинакова для обоих цветов: каждая пустая
        клетка на луче — точка приземления (п.4 movegen.md).
        """

        moves: list[Move] = []
        for delta in self._diagonals:
            next_ndx = ndx + delta
            # Клетки «бортика» не входят в `self._states` (см. `__init__`),
            # поэтому проверка `in` эквивалентна проверке `OUT_OF_BOARD`.
            while next_ndx in self._states and self._states[next_ndx] == SquareState.EMPTY:
                moves.append(
                    Move(
                        # `Move.path` хранит номера игровых полей (1..N),
                        # а не внутренние индексы (пп. 3–4 movegen.md).
                        path=(self._number_of[ndx], self._number_of[next_ndx]),
                        # Для тихого хода `captured` — пустой кортеж,
                        # а не `None`: `Move.captured: tuple[int, ...]`.
                        captured=(),
                    )
                )
                next_ndx += delta
        return moves

    def _generate_black_moves(self) -> list[Move]:
        """Все ходы чорных фигур."""
        moves: list[Move] = []
        for ndx in self._pieces_of(Player.BLACK):
            # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
            if self._states[ndx] == SquareState.BLACK_MAN:
                moves.extend(self._generate_black_man_moves(ndx))
            elif self._states[ndx] == SquareState.BLACK_KING:
                moves.extend(self._generate_black_king_moves(ndx))
        return moves

    def _generate_black_captures(self) -> list[Move]:
        """Все взятия черных фигур."""
        moves: list[Move] = []
        for ndx in self._pieces_of(Player.BLACK):
            if self._states[ndx] == SquareState.BLACK_MAN:
                moves.extend(self._generate_black_man_captures(ndx))
            elif self._states[ndx] == SquareState.BLACK_KING:
                moves.extend(self._generate_black_king_captures(ndx))
        return moves

    def _generate_black_man_captures(self, ndx: int) -> list[Move]:
        """Все взятия чорных простых фигур."""
        moves: list[Move] = []
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
        return moves

    def _generate_black_king_captures(self, ndx: int) -> list[Move]:
        """Все взятия чорных дамок."""
        moves: list[Move] = []
        self._king_captures_from(
            ndx,
            [ndx],
            [],
            moves,
            own=(SquareState.BLACK_MAN, SquareState.BLACK_KING),
            king=SquareState.BLACK_KING,
        )
        return moves

    def _generate_black_man_moves(self, ndx: int) -> list[Move]:
        """Все тихие ходы чёрной простой: проверяем два соседних поля на `EMPTY`.

        Чёрные движутся в сторону увеличения внутренних индексов (вниз
        по доске), поэтому оба соседних поля получаются сложением
        `self._move_left` и `self._move_right`.
        """
        moves: list[Move] = []
        for delta in (self._move_left, self._move_right):
            next_ndx = ndx + delta
            # Клетки «бортика» не входят в `self._states` (см. `__init__`),
            # поэтому проверка `in` эквивалентна проверке `OUT_OF_BOARD`.
            if next_ndx in self._states and self._states[next_ndx] == SquareState.EMPTY:
                moves.append(
                    Move(
                        # `Move.path` хранит номера игровых полей (1..N),
                        # а не внутренние индексы (пп. 3–4 movegen.md).
                        path=(self._number_of[ndx], self._number_of[next_ndx]),
                        # Для тихого хода `captured` — пустой кортеж,
                        # а не `None`: `Move.captured: tuple[int, ...]`.
                        captured=(),
                        # Пешка, завершившая ход на строке превращения,
                        # получает `promotes=True` (п.4 movegen.md).
                        promotes=next_ndx in self._promotion_squares[Player.BLACK],
                    )
                )
        return moves

    def _generate_black_king_moves(self, ndx: int) -> list[Move]:
        """Все тихие ходы чорной дамки: скольжение по всем четырём диагоналям.

        Дамка движется в любом направлении до первого препятствия,
        поэтому геометрия одинакова для обоих цветов: каждая пустая
        клетка на луче — точка приземления (п.4 movegen.md).
        """

        moves: list[Move] = []
        for delta in self._diagonals:
            next_ndx = ndx + delta
            # Клетки «бортика» не входят в `self._states` (см. `__init__`),
            # поэтому проверка `in` эквивалентна проверке `OUT_OF_BOARD`.
            while next_ndx in self._states and self._states[next_ndx] == SquareState.EMPTY:
                moves.append(
                    Move(
                        # `Move.path` хранит номера игровых полей (1..N),
                        # а не внутренние индексы (пп. 3–4 movegen.md).
                        path=(self._number_of[ndx], self._number_of[next_ndx]),
                        # Для тихого хода `captured` — пустой кортеж,
                        # а не `None`: `Move.captured: tuple[int, ...]`.
                        captured=(),
                    )
                )
                next_ndx += delta
        return moves
