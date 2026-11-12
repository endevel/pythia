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

Функция опирается на `MoveGenerator.make_move`/`unmake_move`, поэтому
perft заодно проверяет и корректность отката хода: повреждение позиции
мгновенно отражается в числах.
"""

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.move import Move
from pythia.movegen.rules import Rules


def opponent_of(player: Player) -> Player:
    """Игрок, делающий следующий ход."""
    return Player.BLACK if player == Player.WHITE else Player.WHITE


def perft(generator: MoveGenerator, player: Player, depth: int) -> int:
    """Число листовых узлов дерева игры на глубине `depth`.

    Аргументы:
        generator: генератор ходов в стартовой позиции perft-обхода;
            позиция мутируется и полностью восстанавливается к исходной.
        player: игрок, чей ход в текущей позиции.
        depth: глубина обхода (0 -> 1).
    """
    if depth == 0:
        return 1
    moves = generator.generate(player)
    if depth == 1:
        return len(moves)
    total = 0
    next_player = opponent_of(player)
    for move in moves:
        undo = generator.make_move(move, player)
        total += perft(generator, next_player, depth - 1)
        generator.unmake_move(undo)
    return total


def perft_divide(generator: MoveGenerator, player: Player, depth: int) -> dict[Move, int]:
    """Perft с разбиением по корневым ходам (divide) — для поиска расхождений.

    Возвращает {ход: число узлов поддерева}; сумма значений равна
    `perft(generator, player, depth)`. При несовпадении с эталоном сравнение
    по ходам локализует ветку дерева, в которой ошибка генерации.
    """
    result = {}
    next_player = opponent_of(player)
    for move in generator.generate(player):
        undo = generator.make_move(move, player)
        result[move] = perft(generator, next_player, depth - 1)
        generator.unmake_move(undo)
    return result


def generator_from_fen(fen: str, rules: Rules, board_size: BoardSize) -> MoveGenerator:
    """Создаёт генератор ходов из FEN-строки (PDN) с данными правилами."""
    board = Damboard(board_size)
    board.setup(fen)
    return MoveGenerator(board, rules)
