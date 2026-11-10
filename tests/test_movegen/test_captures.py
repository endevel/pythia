"""Тесты взятий простых и дамок — `_generate_*_captures` (п.4 movegen.md).

Методы вызываются напрямую для одной фигуры: это позволяет проверить
геометрию взятий и DFS-цепочки изолированно от перебора всех фигур.
Внутренний индекс фигуры получается обратным отображением `_number_of`.

Геометрия стандартной доски 8x8 (FMJD-нумерация сверху вниз, по 4 тёмных
поля в ряду): ряд 1 — поля 1–4 (превращение белых), ряд 8 — поля 29–32
(превращение чёрных). Простая бьёт во все четыре диагонали, дамка —
со скольжением по лучу и любым пустым полем приземления за жертвой.
"""

from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.rules import INTERNATIONAL, RUSSIAN, Rules


def _generator(fen: str, rules: Rules = RUSSIAN) -> MoveGenerator:
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    return MoveGenerator(board, rules)


def _ndx(generator: MoveGenerator, square: int) -> int:
    """Внутренний индекс игрового поля `square` (1..N)."""
    return next(
        ndx for ndx in generator._number_of if generator._number_of[ndx] == square
    )


def _moves(moves) -> set[tuple[tuple[int, ...], tuple[int, ...], bool]]:
    """Ходы в виде {(path, captured, promotes)} — для сравнения множеств."""
    return {(move.path, move.captured, move.promotes) for move in moves}


# --- _generate_white_man_captures ---------------------------------------


def test_white_man_single_capture_forward():
    # Простая 26 бьёт 22 сверху-слева: приземление строго за жертвой — поле 17.
    generator = _generator("W:W26:B22.")
    moves = generator._generate_white_man_captures(_ndx(generator, 26))
    assert _moves(moves) == {((26, 17), (22,), False)}


def test_white_man_captures_in_both_forward_directions():
    # Простая 23 бьёт 18 (приземление 14) и 19 (приземление 16).
    generator = _generator("W:W23:B18,19.")
    moves = generator._generate_white_man_captures(_ndx(generator, 23))
    assert _moves(moves) == {((23, 14), (18,), False), ((23, 16), (19,), False)}


def test_white_man_captures_backward():
    # Простая бьёт во все стороны: 23 бьёт 27 назад, приземление 32.
    generator = _generator("W:W23:B27.")
    moves = generator._generate_white_man_captures(_ndx(generator, 23))
    assert _moves(moves) == {((23, 32), (27,), False)}


def test_white_man_capture_blocked_by_own_piece_on_landing():
    # Жертва 22 есть, но поле приземления 17 занято своей простой —
    # взятия нет, метод возвращает пустой список.
    generator = _generator("W:W26,17:B22.")
    moves = generator._generate_white_man_captures(_ndx(generator, 26))
    assert moves == []


def test_white_man_without_captures_returns_empty_list():
    # Чёрная на 1 не стоит ни на одной диагонали простой 26.
    generator = _generator("W:W26:B1.")
    moves = generator._generate_white_man_captures(_ndx(generator, 26))
    assert moves == []


def test_white_man_double_capture_chain():
    # Цепочка: 28 x 24 -> 19, затем 19 x 15 -> 10; с поля 10 продолжить
    # бой нечем (битая 15 не бьётся вторично, других жертв нет).
    generator = _generator("W:W28:B24,15.")
    moves = generator._generate_white_man_captures(_ndx(generator, 28))
    assert _moves(moves) == {((28, 19, 10), (24, 15), False)}


def test_white_man_promotes_when_capture_ends_on_king_row():
    # 10 x 6 -> поле 1 (строка превращения): ход завершается превращением,
    # продолжить бой дамке не с чего — единственный ход с promotes=True.
    generator = _generator("W:W10:B6.")
    moves = generator._generate_white_man_captures(_ndx(generator, 10))
    assert _moves(moves) == {((10, 1), (6,), True)}


def test_white_man_promotes_at_once_and_continues_as_king():
    # Русские шашки: 11 x 7 -> поле 2 (превращение), далее дамка бьёт 6 по
    # лучу 2–6–9–13 и может встать на 9 или 13; оба хода promotes=True.
    generator = _generator("W:W11:B6,7.")
    moves = generator._generate_white_man_captures(_ndx(generator, 11))
    assert _moves(moves) == {
        ((11, 2, 9), (7, 6), True),
        ((11, 2, 13), (7, 6), True),
    }


def test_white_man_international_continues_as_man_after_promotion_square():
    # Международные: с поля превращения 2 бой продолжается как простой
    # (жертва 6, посадка 9), простая остаётся простой — promotes=False.
    generator = _generator("W:W11:B6,7.", INTERNATIONAL)
    moves = generator._generate_white_man_captures(_ndx(generator, 11))
    assert _moves(moves) == {((11, 2, 9), (7, 6), False)}


# --- _generate_white_king_captures --------------------------------------


def test_white_king_single_capture_any_landing_behind_victim():
    # Дамка 19 бьёт 23 по лучу 19–23–26–30 и может встать на 26 или 30.
    generator = _generator("W:WK19:B23.")
    moves = generator._generate_white_king_captures(_ndx(generator, 19))
    assert _moves(moves) == {((19, 26), (23,), False), ((19, 30), (23,), False)}


def test_white_king_long_range_capture():
    # Дамка 1 скользит по лучу 1–5–9–15–19 до жертвы 24, посадка — 28.
    generator = _generator("W:WK1:B24.")
    moves = generator._generate_white_king_captures(_ndx(generator, 1))
    assert _moves(moves) == {((1, 28), (24,), False)}


def test_white_king_landing_on_own_piece_is_excluded():
    # Своя простая на 30 перерезает луч за жертвой 23 — остаётся посадка 26.
    generator = _generator("W:WK19,30:B23.")
    moves = generator._generate_white_king_captures(_ndx(generator, 19))
    assert _moves(moves) == {((19, 26), (23,), False)}


def test_white_king_capture_blocked_by_piece_behind_victim():
    # Сразу за жертвой 23 стоит чёрная 26 — полей приземления нет, взятия нет.
    generator = _generator("W:WK19:B23,26.")
    moves = generator._generate_white_king_captures(_ndx(generator, 19))
    assert moves == []


def test_white_king_captures_backward():
    # Дамка 23 бьёт 27 назад, приземление 32.
    generator = _generator("W:WK23:B27.")
    moves = generator._generate_white_king_captures(_ndx(generator, 23))
    assert _moves(moves) == {((23, 32), (27,), False)}


def test_white_king_double_capture_branches_free_choice():
    # Русские (FREE_CHOICE): дамка 19 бьёт 23; остановка на 30 даёт ход
    # (19, 30), остановка на 26 продолжает бой через 22 до 17 или 13.
    generator = _generator("W:WK19:B22,23.")
    moves = generator._generate_white_king_captures(_ndx(generator, 19))
    assert _moves(moves) == {
        ((19, 30), (23,), False),
        ((19, 26, 17), (23, 22), False),
        ((19, 26, 13), (23, 22), False),
    }


def test_white_king_international_max_majority_filter():
    # Международные (MAX_MAJORITY): остаются только взятия с максимумом
    # побитых — цепочки (19, 26, 17) и (19, 26, 13).
    generator = _generator("W:WK19:B22,23.", INTERNATIONAL)
    moves = generator._generate_white_king_captures(_ndx(generator, 19))
    assert _moves(moves) == {
        ((19, 26, 17), (23, 22), False),
        ((19, 26, 13), (23, 22), False),
    }


# --- _generate_black_man_captures ---------------------------------------


def test_black_man_single_capture_forward():
    # Чёрная простая 12 бьёт 16, приземление 19.
    generator = _generator("B:B12:W16.")
    moves = generator._generate_black_man_captures(_ndx(generator, 12))
    assert _moves(moves) == {((12, 19), (16,), False)}


def test_black_man_captures_in_both_forward_directions():
    # Простая 18 бьёт 22 (приземление 25) и 23 (приземление 27).
    generator = _generator("B:B18:W22,23.")
    moves = generator._generate_black_man_captures(_ndx(generator, 18))
    assert _moves(moves) == {((18, 25), (22,), False), ((18, 27), (23,), False)}


def test_black_man_captures_backward():
    # Простая бьёт во все стороны: 18 бьёт 14 назад, приземление 9.
    generator = _generator("B:B18:W14.")
    moves = generator._generate_black_man_captures(_ndx(generator, 18))
    assert _moves(moves) == {((18, 9), (14,), False)}


def test_black_man_capture_blocked_by_own_piece_on_landing():
    # Жертва 16 есть, но поле приземления 19 занято своей простой.
    generator = _generator("B:B12,19:W16.")
    moves = generator._generate_black_man_captures(_ndx(generator, 12))
    assert moves == []


def test_black_man_double_capture_chain():
    # Цепочка: 12 x 16 -> 19, затем 19 x 24 -> 28.
    generator = _generator("B:B12:W16,24.")
    moves = generator._generate_black_man_captures(_ndx(generator, 12))
    assert _moves(moves) == {((12, 19, 28), (16, 24), False)}


def test_black_man_international_max_majority_and_promotion():
    # Международные: из двух взятий остаётся длинное (13, 22, 31); простая
    # не может продолжить бой с поля превращения 31 и завершает ход
    # превращением — promotes=True.
    generator = _generator("B:B13:W17,26.", INTERNATIONAL)
    moves = generator._generate_black_man_captures(_ndx(generator, 13))
    assert _moves(moves) == {((13, 22, 31), (17, 26), True)}


# --- _generate_black_king_captures --------------------------------------


def test_black_king_single_capture_any_landing_behind_victim():
    # Дамка 10 бьёт 19 по лучу 10–15–19–24–28; посадки — 24 и 28.
    generator = _generator("B:BK10:W19.")
    moves = generator._generate_black_king_captures(_ndx(generator, 10))
    assert _moves(moves) == {((10, 24), (19,), False), ((10, 28), (19,), False)}


def test_black_king_landing_and_continuation_free_choice():
    # Дамка 26 бьёт 19 по лучу 26–23–19–16–12; с посадки 16 бой
    # продолжается через жертву 7 до поля 2, с посадки 12 продолжения нет
    # (жертва 19 не бьётся вторично — TAKEN не сканируется).
    generator = _generator("B:BK26:W7,19.")
    moves = generator._generate_black_king_captures(_ndx(generator, 26))
    assert _moves(moves) == {((26, 16, 2), (19, 7), False), ((26, 12), (19,), False)}


def test_black_king_international_max_majority_filter():
    # Международные: остаётся только цепочка из двух побитых шашек.
    generator = _generator("B:BK26:W7,19.", INTERNATIONAL)
    moves = generator._generate_black_king_captures(_ndx(generator, 26))
    assert _moves(moves) == {((26, 16, 2), (19, 7), False)}
