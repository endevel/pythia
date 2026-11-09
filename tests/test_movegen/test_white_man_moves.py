"""Тесты тихих ходов белой простой — п.4 movegen.md.

Тестируем наблюдаемое поведение через публичный `MoveGenerator.generate`
на позициях без возможных взятий: взятие обязательно, поэтому при его
наличии тихие ходы не генерируются вовсе. Все позиции подобраны так,
что ни одна простая не может никого побить (за каждой чужой фигурой,
стоящей на передней диагонали, своя шашка перекрывает поле приземления).
"""

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.move import Move
from pythia.movegen.rules import RUSSIAN


def _quiet_moves(fen: str, player: Player = Player.WHITE) -> dict[tuple[int, int], Move]:
    """Тихие ходы игрока в позиции `fen` в виде {(откуда, куда): Move}."""
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    generator = MoveGenerator(board, RUSSIAN)
    return {(move.path[0], move.path[-1]): move for move in generator.generate(player)}


def test_man_in_center_moves_to_both_forward_diagonals():
    # Простая на 26 (внутр. 74): передние диагонали — поля 22 и 23.
    moves = _quiet_moves("W:W26:B1.")
    assert set(moves) == {(26, 22), (26, 23)}


def test_man_blocked_by_own_piece_has_single_forward_move():
    # Своя простая на 23 перекрывает одну из передних диагоналей поля 26;
    # сама простая 23 ходит на 18 и 19. Назад (на 26/27) хода нет.
    moves = _quiet_moves("W:W26,23:B1.")
    assert set(moves) == {(26, 22), (23, 18), (23, 19)}


def test_man_blocked_by_enemy_piece_has_single_forward_move():
    # Чужая простая на 22 занимает переднюю диагональ поля 26; поле
    # приземления за ней (17) занято своей простой, поэтому взятий в
    # позиции нет и остаются тихие ходы с учётом блокировки направления.
    moves = _quiet_moves("W:W26,17:B1,22.")
    assert set(moves) == {(26, 23), (17, 13), (17, 14)}


def test_man_on_right_edge_moves_to_single_forward_square():
    # Простая на 28 (внутр. 78, правый край): вперёд-вправо света нет,
    # единственная передняя диагональ — поле 24.
    moves = _quiet_moves("W:W28:B1.")
    assert set(moves) == {(28, 24)}


def test_man_on_left_edge_moves_to_single_forward_square():
    # Простая на 21 (внутр. 61, левый край): вперёд-влево света нет,
    # единственная передняя диагональ — поле 17.
    moves = _quiet_moves("W:W21:B1.")
    assert set(moves) == {(21, 17)}


def test_man_promotes_on_last_row():
    # Простая на 6 ходит на поля 1 и 2 верхней горизонтали — оба хода
    # завершаются на строке превращения: `promotes=True` (п.4 movegen.md).
    moves = _quiet_moves("W:W6:B12.")
    assert set(moves) == {(6, 1), (6, 2)}
    assert all(move.promotes for move in moves.values())


def test_quiet_move_has_empty_captured_and_no_promotion():
    # Тихий ход вне дамочной строки: `captured` — пустой кортеж,
    # `promotes` — False.
    moves = _quiet_moves("W:W26:B1.")
    for move in moves.values():
        assert move.captured == ()
        assert move.promotes is False


def test_moves_of_all_men_are_collected():
    # Две простые в центре: каждая даёт по два хода на свободные поля.
    moves = _quiet_moves("W:W26,27:B1.")
    assert set(moves) == {(26, 22), (26, 23), (27, 23), (27, 24)}


def test_black_man_moves_downward():
    # Симметрия: чёрная простая на 1 ходит в сторону увеличения индексов —
    # на поля 5 и 6 (белая простая на 32 в генерации не участвует).
    moves = _quiet_moves("B:B1:W32.", Player.BLACK)
    assert set(moves) == {(1, 5), (1, 6)}
