"""Тесты применения и отката хода — make_move/unmake_move (п.4 search.md).

Геометрия стандартной доски: ряд 1 — поля 1–4 (превращение белых).
"""

from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.move import Move
from pythia.movegen.rules import RUSSIAN


def _generator(fen: str) -> MoveGenerator:
    board = Damboard(BoardSize.STANDARD)
    board.setup(fen)
    return MoveGenerator(board, RUSSIAN)


def _ndx(generator: MoveGenerator, square: int) -> int:
    return generator.ndx_of(square)


def test_make_and_unmake_quiet_move():
    # Тихий ход 23 -> 19: фигура уходит с исходного поля на поле
    # приземления; откат восстанавливает позицию в точности.
    generator = _generator("W:W23:B18.")
    origin, landing = _ndx(generator, 23), _ndx(generator, 19)
    undo = generator.make_move(Move(path=(23, 19), captured=()), Player.WHITE)
    assert generator.state(origin) == SquareState.EMPTY
    assert generator.state(landing) == SquareState.WHITE_MAN
    generator.unmake_move(undo)
    assert generator.state(origin) == SquareState.WHITE_MAN
    assert generator.state(landing) == SquareState.EMPTY


def test_make_and_unmake_capture():
    # Взятие 23x18 -> 14: ход завершён, побитая фигура снята с доски —
    # её поле становится EMPTY (обычной пустой клеткой для следующего
    # хода); откат возвращает и жертву, и ходившую фигуру.
    generator = _generator("W:W23:B18.")
    origin = _ndx(generator, 23)
    victim = _ndx(generator, 18)
    landing = _ndx(generator, 14)
    undo = generator.make_move(Move(path=(23, 14), captured=(18,)), Player.WHITE)
    assert generator.state(origin) == SquareState.EMPTY
    assert generator.state(victim) == SquareState.EMPTY
    assert generator.state(landing) == SquareState.WHITE_MAN
    generator.unmake_move(undo)
    assert generator.state(origin) == SquareState.WHITE_MAN
    assert generator.state(victim) == SquareState.BLACK_MAN
    assert generator.state(landing) == SquareState.EMPTY


def test_make_and_unmake_promotion():
    # Тихий ход 5 -> 1 с превращением: на поле приземления — дамка;
    # откат возвращает простую на исходное поле.
    generator = _generator("W:W5:B18.")
    origin, landing = _ndx(generator, 5), _ndx(generator, 1)
    undo = generator.make_move(Move(path=(5, 1), captured=(), promotes=True), Player.WHITE)
    assert generator.state(landing) == SquareState.WHITE_KING
    generator.unmake_move(undo)
    assert generator.state(origin) == SquareState.WHITE_MAN
    assert generator.state(landing) == SquareState.EMPTY


def test_make_and_unmake_black_capture():
    # Зеркальный случай: чёрная 18 бьёт 23 с приземлением на 27.
    # Ход завершён — побитая фигура снята, её поле EMPTY.
    generator = _generator("W:W23:B18.")
    origin = _ndx(generator, 18)
    victim = _ndx(generator, 23)
    landing = _ndx(generator, 27)
    undo = generator.make_move(Move(path=(18, 27), captured=(23,)), Player.BLACK)
    assert generator.state(victim) == SquareState.EMPTY
    assert generator.state(landing) == SquareState.BLACK_MAN
    generator.unmake_move(undo)
    assert generator.state(origin) == SquareState.BLACK_MAN
    assert generator.state(victim) == SquareState.WHITE_MAN
    assert generator.state(landing) == SquareState.EMPTY
