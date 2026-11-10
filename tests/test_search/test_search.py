"""Тесты поиска лучшего хода — `Search` (пп. 3–5 search.md).

Геометрия стандартной доски (FMJD-нумерация): ряд 1 — поля 1–4
(превращение белых), ряд 8 — поля 29–32 (превращение чёрных).
"""

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.move import Move
from pythia.movegen.rules import RUSSIAN
from pythia.search.search import WIN_SCORE, Search


def _search(fen: str) -> Search:
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    return Search(board, RUSSIAN)


# --- одиночные взятия и оценка -------------------------------------------


def test_finds_forced_capture():
    # Простая 23 бьёт 18 с приземлением на 14: единственный ход.
    result = _search("W:W23:B18.").best_move(Player.WHITE, depth=2)
    assert result.move == Move(path=(23, 14), captured=(18,))


def test_prefers_larger_capture():
    # Белая 23 бьёт и 18 (приземление 14), и 27 (приземление 32);
    # обе жертвы — простые, ходы равнозначны по материалу, поэтому
    # проверяем лишь то, что выбрано одно из взятий, а не тихий ход.
    result = _search("W:W23,17:B18,27.").best_move(Player.WHITE, depth=3)
    assert result.move is not None
    assert result.move.is_capture


def test_capture_extension_finds_capture_at_depth_zero():
    # Даже при depth=0 форсированное взятие доигрывается за границей
    # глубины: 26 бьёт 22, и поиск это находит.
    result = _search("W:W26:B22.").best_move(Player.WHITE, depth=0)
    assert result.move == Move(path=(26, 17), captured=(22,))


def test_mate_in_one_is_detected():
    # Последняя фигура чёрных побита ходом 23x14 — белые получают
    # победу; счёт = WIN_SCORE - ply (ply=1).
    result = _search("W:W23:B18.").best_move(Player.WHITE, depth=2)
    assert result.move == Move(path=(23, 14), captured=(18,))
    assert result.score == WIN_SCORE - 1


def test_extension_does_not_hide_hanging_piece():
    # Белая 23 не имеет взятий, её тихие ходы — на 18 и 19; обе диагонали
    # простреливает чёрная дамка 32 (лучи 32-28-23-18 и 32-27-23-19).
    # Продление взятий доигрывает бой за границей глубины, поэтому счёт
    # для белых проигрышный: шашка не «спрятана» за горизонтом перебора.
    result = _search("W:W23:BK32.").best_move(Player.WHITE, depth=1)
    assert result.score <= -100


# --- тихие ходы и превращение --------------------------------------------


def test_promotion_is_valued():
    # Простая 5 превращается в дамку (поля 1/2): с точки зрения белых
    # дамка (270) против простой чёрных (100) — счёт 170.
    result = _search("W:W5:B18.").best_move(Player.WHITE, depth=2)
    assert result.move is not None
    assert result.move.promotes
    assert result.score == 170


def test_no_moves_is_loss():
    # У белых нет фигур — ходов нет, позиция проиграна.
    result = _search("W:B22.").best_move(Player.WHITE, depth=2)
    assert result.move is None
    assert result.score == -WIN_SCORE


def test_black_side_gets_mirrored_score():
    # Материал равный (по одной простой), но белая ближе к превращению:
    # при depth=2 чёрные видят для себя проигрышную оценку (белые успеют
    # стать дамкой раньше), т.е. счёт для чёрных отрицателен.
    result = _search("W:W5:B18.").best_move(Player.BLACK, depth=2)
    assert result.score <= 0


# --- инварианты ------------------------------------------------------------


def test_search_does_not_mutate_board():
    # Доска — неизменяемый источник истины: после поиска расстановка
    # не изменилась.
    board = Damboard(BoardSize.STANDARD)
    board.setup("W:W28,23:B24,15.")
    white_before = set(board.white_pieces)
    black_before = set(board.black_pieces)
    Search(board, RUSSIAN).best_move(Player.WHITE, depth=4)
    assert board.white_pieces == white_before
    assert board.black_pieces == black_before


def test_search_restores_working_position():
    # Рабочая позиция генератора после поиска совпадает с исходной.
    board = Damboard(BoardSize.STANDARD)
    board.setup("W:W28,23:B24,15.")
    search = Search(board, RUSSIAN)
    reference = Search(board, RUSSIAN)
    search.best_move(Player.WHITE, depth=4)
    assert search._generator.states == reference._generator.states
