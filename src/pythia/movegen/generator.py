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
        for ndx in self._pieces_of(Player.BLACK):
            # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
            if self._states[ndx] == SquareState.BLACK_MAN:
                moves.extend(self._generate_white_man_captures(ndx))
            elif self._states[ndx] == SquareState.BLACK_KING:
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
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
        return moves

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
        """Все ходы белых дамок."""
        moves: list[Move] = []
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
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
            # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
            pass
        return moves

    def _generate_black_man_captures(self, ndx: int) -> list[Move]:
        """Все взятия чорных простых фигур."""
        moves: list[Move] = []
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
        return moves

    def _generate_black_king_captures(self, ndx: int) -> list[Move]:
        """Все взятия чорных дамок."""
        moves: list[Move] = []
        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
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
        """Все ходы чорных дамок."""
        moves: list[Move] = []
        return moves

        # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
