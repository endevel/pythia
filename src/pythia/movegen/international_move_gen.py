from pythia.core.move import Move
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import BaseMoveGenerator, GenerateMoveList
from pythia.movegen.standard.black_man_move import BlackManMove
from pythia.movegen.standard.international_man_capture import InternationalManCapture
from pythia.movegen.standard.king_capture import KingCapture
from pythia.movegen.standard.king_move import KingMove
from pythia.movegen.standard.white_man_move import WhiteManMove


class InternationalMoveGen(GenerateMoveList):
    """Генератор ходов по правилам международных шашек.

    Для каждого типа фигуры игрока используется отдельный генератор:
    простые шашки и дамки ходят и бьют по разным правилам. Взятие в
    международных шашках обязательно, поэтому тихие ходы рассматриваются
    только при отсутствии ударных, а из ударных остаются лишь те, что
    снимают максимальное число фигур противника.
    """

    def __init__(self, board: DamBoard, player: Player):
        self._board = board
        self._player = player
        if player == Player.WHITE:
            self._man_move_gen: BaseMoveGenerator = WhiteManMove(board)
            self._king_move_gen: BaseMoveGenerator = KingMove(board)
            self._man_capture_gen: BaseMoveGenerator = InternationalManCapture(board)
            self._king_capture_gen: BaseMoveGenerator = KingCapture(board)
        else:
            self._man_move_gen: BaseMoveGenerator = BlackManMove(board)
            self._king_move_gen: BaseMoveGenerator = KingMove(board)
            self._man_capture_gen: BaseMoveGenerator = InternationalManCapture(board)
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
        шашек используется :class:`InternationalManCapture`, для дамок —
        :class:`KingCapture`. Поскольку взятие обязательно и должно быть
        максимальным, из найденных цепочек остаются только снимающие
        наибольшее число фигур противника.
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

        if not captures:
            return captures

        max_taken = max(len(move.taken) for move in captures)
        return [move for move in captures if len(move.taken) == max_taken]

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
                moves.extend(self._man_move_gen.generate_moves(self._board, square_ndx))
            elif state is king_state:
                moves.extend(
                    self._king_move_gen.generate_moves(self._board, square_ndx)
                )
        return moves

    def generate_move_list(self) -> list[Move]:
        """Возвращает список допустимых ходов игрока, чей ход.

        Взятие в международных шашках обязательно, поэтому при наличии
        ударных ходов возвращаются только они. Среди ударных ходов
        генератор :meth:`_generate_captures` оставляет лишь цепочки,
        снимающие максимальное число фигур противника.
        """

        captures = self._generate_captures()
        if captures:
            return captures
        return self._generate_moves()
