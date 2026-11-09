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
        for ndx in self._pieces_of(player):
            # Перебор фигур игрока: здесь будет поиск ходов каждой фигуры.
            pass
        raise NotImplementedError("Генерация ходов — п.4 movegen.md")

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
