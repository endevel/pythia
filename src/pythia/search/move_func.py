from pythia.core.move import Move
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard

_WHITE_STATES = (SquareState.WHITE_MAN, SquareState.WHITE_KING)
_BLACK_STATES = (SquareState.BLACK_MAN, SquareState.BLACK_KING)


def _owner(state: SquareState) -> Player:
    """Возвращает владельца фигуры по состоянию клетки."""

    if state in _WHITE_STATES:
        return Player.WHITE
    if state in _BLACK_STATES:
        return Player.BLACK
    raise ValueError(f"Клетка не содержит фигуры: {state}")


def _opponent(player: Player) -> Player:
    """Возвращает игрока, который ходит следующим."""

    return Player.BLACK if player == Player.WHITE else Player.WHITE


def do_move(board: DamBoard, move: Move):
    """Применяет ход к доске.

    Фигура снимается с исходной клетки, все взятые фигуры удаляются с
    доски, а на клетке назначения устанавливается состояние
    ``move.after_state``. Это состояние уже учитывает превращение простой
    шашки в дамку, поэтому отдельная проверка дамочного ряда не нужна.

    После хода очередь переходит сопернику владельца ходившей фигуры.

    Args:
        board: Доска, к которой применяется ход.
        move: Ход, содержащий исходную и конечную клетки, состояния
            фигуры до и после хода, а также список взятых фигур.
    """

    player = _owner(move.before_state)

    board.set_state(move.from_square, SquareState.EMPTY)
    for taken_ndx, _ in move.taken:
        board.set_state(taken_ndx, SquareState.EMPTY)
    board.set_state(move.to_square, move.after_state)
    board.player_to_move = _opponent(player)


def undo_move(board: DamBoard, move: Move):
    """Отменяет ранее применённый ход, восстанавливая позицию доски.

    На клетке назначения фигура убирается, на исходную клетку возвращается
    состояние ``move.before_state``, а все взятые фигуры восстанавливаются
    с сохранёнными состояниями. Очередь хода возвращается владельцу
    ходившей фигуры.

    Args:
        board: Доска, к которой был применён ход.
        move: Ход, который нужно отменить.
    """

    player = _owner(move.before_state)

    board.set_state(move.to_square, SquareState.EMPTY)
    for taken_ndx, taken_state in reversed(move.taken):
        board.set_state(taken_ndx, taken_state)
    board.set_state(move.from_square, move.before_state)
    board.player_to_move = player
