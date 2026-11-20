from pythia.core.move import Move
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator
from pythia.movegen.standard.black_man_move import BlackManMove
from pythia.movegen.standard.king_capture import KingCapture
from pythia.movegen.standard.king_move import KingMove
from pythia.movegen.standard.russian_man_capture import RussianManCapture
from pythia.movegen.standard.white_man_move import WhiteManMove


class RussianMoveGen:
    """Генератор ходов по правилам русских шашек.

    Для каждого типа фигуры игрока используется отдельный генератор:
    простые шашки и дамки ходят и бьют по разным правилам. Взятие в
    русских шашках обязательно, поэтому тихие ходы рассматриваются только
    при отсутствии ударных.

    Главное отличие от международных шашек состоит в выборе боя: игрок
    вправе взять любой доступный вариант, а не только снимающий
    максимальное число фигур противника. Поэтому найденные цепочки
    возвращаются без фильтра по количеству снятых фигур.
    """

    def __init__(self, board: DamBoard, player: Player):
        self._board = board
        self._player = player
        if player == Player.WHITE:
            self._man_move_gen: BaseMoveGenerator = WhiteManMove(board)
        else:
            self._man_move_gen: BaseMoveGenerator = BlackManMove(board)
        self._king_move_gen: BaseMoveGenerator = KingMove(board)
        self._man_capture_gen: BaseMoveGenerator = RussianManCapture(board)
        self._king_capture_gen: BaseMoveGenerator = KingCapture(board)

    def _piece_states(self) -> tuple[SquareState, SquareState]:
        """Возвращает состояния простой шашки и дамки игрока, чей ход."""

        if self._player == Player.WHITE:
            return SquareState.WHITE_MAN, SquareState.WHITE_KING
        return SquareState.BLACK_MAN, SquareState.BLACK_KING

    def _player_squares(self) -> list[int]:
        """Возвращает внутренние индексы клеток с фигурами игрока, чей ход.

        Свойства :attr:`DamBoard.white_pieces` и :attr:`DamBoard.black_pieces`
        содержат номера игровых полей (1..N), тогда как генераторы работают
        с внутренними индексами плоского массива. Номера переводятся через
        :meth:`DamBoard.ndx_of_number`, поэтому перебираются только клетки
        с фигурами игрока, а не вся доска.
        """

        if self._player == Player.WHITE:
            numbers = self._board.white_pieces
        else:
            numbers = self._board.black_pieces
        return sorted(self._board.ndx_of_number(number) for number in numbers)

    def _generate_captures(self) -> list[Move]:
        """Возвращает ударные ходы игрока, чей ход.

        Перебираются все клетки доски с фигурами игрока: для простых
        шашек используется :class:`RussianManCapture`, для дамок —
        :class:`KingCapture`. В отличие от международных шашек фильтр по
        максимальному числу снятых фигур не применяется: допустим любой
        вариант боя.
        """

        man_state, king_state = self._piece_states()
        captures: list[Move] = []
        for square_ndx in self._player_squares():
            state = self._board[square_ndx]
            if state is man_state:
                captures.extend(
                    self._man_capture_gen.generate_moves(self._board, square_ndx)
                )
            elif state is king_state:
                captures.extend(
                    self._king_capture_gen.generate_moves(self._board, square_ndx)
                )
        return captures

    def _generate_moves(self) -> list[Move]:
        """Возвращает тихие ходы игрока, чей ход.

        Для простых шашек используется :class:`WhiteManMove` или
        :class:`BlackManMove` (в зависимости от цвета), для дамок —
        :class:`KingMove`.
        """

        man_state, king_state = self._piece_states()
        moves: list[Move] = []
        for square_ndx in self._player_squares():
            state = self._board[square_ndx]
            if state is man_state:
                moves.extend(
                    self._man_move_gen.generate_moves(self._board, square_ndx)
                )
            elif state is king_state:
                moves.extend(
                    self._king_move_gen.generate_moves(self._board, square_ndx)
                )
        return moves

    def generate_move_list(self) -> list[Move]:
        """Возвращает список допустимых ходов игрока, чей ход.

        Если у игрока есть хотя бы один ударный ход, возвращаются только
        они: взятие обязательно. В противном случае возвращаются тихие
        ходы. Все найденные цепочки взятий считаются допустимыми, даже
        если снимают меньше фигур, чем другие.
        """

        captures = self._generate_captures()
        if captures:
            return captures
        return self._generate_moves()

    # Имя с опечаткой сохранено для совместимости с InternationalMoveGen,
    # у которого исторически используется именно такое написание.
    genarate_move_list = generate_move_list
