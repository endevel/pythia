"""Perft (performance test) — инструмент валидации генератора ходов.

Perft считает общее число листовых узлов дерева игры на заданной глубине.
Эталонные значения для стартовых позиций совпадают у независимых движков
(Scan, Flux, pydraughts и др.):

Международные шашки (10×10, 20+20 шашек):

    perft(1) = 9        perft(5) = 27 117      perft(9)  = 40 050 160
    perft(2) = 81       perft(6) = 167 140      perft(10) = 254 533 352
    perft(3) = 658      perft(7) = 1 049 442
    perft(4) = 4 265    perft(8) = 6 483 961

Русские шашки (8×8, 12+12 шашек):

    perft(1) = 7        perft(5) = 7 482        perft(9)  = 4 570 712
    perft(2) = 49       perft(6) = 37 986       perft(10) = 22 456 537
    perft(3) = 302      perft(7) = 190 146
    perft(4) = 1 469    perft(8) = 929 907

Любое расхождение указывает на ошибку в генерации ходов (правило
большинства, поведение простой на дамочном поле в цепочке взятия,
дамочные ходы и т.д.).

В отличие от эталонного модуля ``pythia_agent``, здесь нет единого класса
``MoveGenerator``: генератор ходов создаётся для конкретной доски и игрока
(:class:`~pythia.movegen.base.GenerateMoveList`), а ход применяется и
отменяется функциями :func:`~pythia.search.move_func.do_move` и
:func:`~pythia.search.move_func.undo_move`. Поэтому perft заодно проверяет
и корректность отката хода: повреждение позиции мгновенно отражается в
числах.
"""

from collections.abc import Callable

from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.player import Player
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import GenerateMoveList
from pythia.movegen.russian_move_gen import RussianMoveGen
from pythia.search.move_func import do_move, undo_move

# Фабрика генератора ходов: класс или экземпляр, принимающий (board, player).
MoveGenFactory = Callable[[DamBoard, Player], GenerateMoveList]


def _numbers(numbers: range) -> str:
    """Собирает секцию FEN из номеров полей через запятую."""

    return ",".join(str(number) for number in numbers)


# Начальные расстановки в нотации проекта: белые занимают нижние ряды,
# чёрные — верхние. Доска 8×8 содержит 32 игровых поля, 10×10 — 50.
RUSSIAN_START_FEN = f"W:W{_numbers(range(21, 33))}:B{_numbers(range(1, 13))}"
INTERNATIONAL_START_FEN = (
    f"W:W{_numbers(range(31, 51))}:B{_numbers(range(1, 21))}"
)


def opponent_of(player: Player) -> Player:
    """Игрок, делающий следующий ход."""

    return Player.BLACK if player == Player.WHITE else Player.WHITE


def _factory(movegen: MoveGenFactory | GenerateMoveList) -> MoveGenFactory:
    """Возвращает фабрику генератора по классу или экземпляру."""

    if isinstance(movegen, type):
        return movegen
    return type(movegen)


def board_from_fen(
    fen: str, board_size: BoardSize = BoardSize.STANDARD
) -> DamBoard:
    """Создаёт доску с позицией из FEN-строки (PDN).

    Аргументы:
        fen: строка позиции в формате FEN (PDN).
        board_size: размер доски (по умолчанию STANDARD 8×8).
    """

    board = DamBoard(board_size=board_size)
    board.setup(fen)
    return board


def perft(
    board: DamBoard,
    player: Player,
    depth: int,
    movegen: MoveGenFactory | GenerateMoveList = RussianMoveGen,
) -> int:
    """Число листовых узлов дерева игры на глубине ``depth``.

    Аргументы:
        board: стартовая позиция perft-обхода; позиция мутируется и
            полностью восстанавливается к исходной.
        player: игрок, чей ход в текущей позиции.
        depth: глубина обхода (``0`` -> ``1``).
        movegen: класс или экземпляр генератора ходов. Для каждой позиции
            создаётся новый экземпляр того же типа, поскольку генератор
            привязан к конкретной доске и игроку.

    Исключения:
        ValueError: если ``depth`` отрицательна.
    """

    if depth < 0:
        raise ValueError("Глубина perft не может быть отрицательной")

    if depth == 0:
        return 1

    factory = _factory(movegen)
    moves = factory(board, player).generate_move_list()

    if depth == 1:
        return len(moves)

    total = 0
    next_player = opponent_of(player)
    for move in moves:
        do_move(board, move)
        total += perft(board, next_player, depth - 1, factory)
        undo_move(board, move)
    return total


def perft_divide(
    board: DamBoard,
    player: Player,
    depth: int,
    movegen: MoveGenFactory | GenerateMoveList = RussianMoveGen,
) -> list[tuple[Move, int]]:
    """Perft с разбиением по корневым ходам (divide) — для поиска расхождений.

    Возвращает список пар ``(ход, число узлов поддерева)``; сумма значений
    равна ``perft(board, player, depth, movegen)``. При несовпадении с
    эталоном сравнение по ходам локализует ветку дерева, в которой ошибка
    генерации.

    Используется список, а не словарь, потому что :class:`Move` содержит
    изменяемое поле ``taken`` и не является хэшируемым.

    Исключения:
        ValueError: если ``depth`` меньше единицы.
    """

    if depth < 1:
        raise ValueError("Глубина perft_divide должна быть не меньше 1")

    factory = _factory(movegen)
    result: list[tuple[Move, int]] = []
    next_player = opponent_of(player)
    for move in factory(board, player).generate_move_list():
        do_move(board, move)
        result.append((move, perft(board, next_player, depth - 1, factory)))
        undo_move(board, move)
    return result
