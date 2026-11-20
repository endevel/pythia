from collections.abc import Callable

from pythia.core.board_size import BoardSize
from pythia.core.piece import Piece
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.square_builders.standard_builder import build_standard_board
from pythia.pdn.fen import Fen, fen_from_states


class DamBoard:
    """Доска для игры в шашки.

    Хранит плоский массив клеток, карту соответствия между номерами
    игровых полей (1..N) и внутренними индексами массива, а также
    множества индексов белых и чёрных фигур.
    """

    def __init__(
        self,
        board_size: BoardSize = BoardSize.STANDARD,
        board_init: Callable[
            [BoardSize, list[SquareState], list[int]], None
        ] = build_standard_board,
    ):
        """Создаёт доску и заполняет её начальной расстановкой.

        Args:
            board_size: Размер доски (по умолчанию STANDARD).
            board_init: Функция инициализации, заполняющая плоский массив
                клеток и карту соответствия номеров полей индексам.
        """

        self._board_size = board_size
        self._squares = []
        self._board_map = []
        self._number_map: dict[int, int] = {}
        self._white_pieces = set()
        self._black_pieces = set()
        self._board_init = board_init
        self._player_to_move = Player.WHITE
        board_init(self._board_size, self._squares, self._board_map)
        self._rebuild_number_map()

    def _rebuild_number_map(self):
        """Перестраивает обратное отображение: внутренний индекс -> номер поля."""

        self._number_map = {
            ndx: number + 1 for number, ndx in enumerate(self._board_map)
        }

    def __getitem__(self, index):
        """Возвращает состояние клетки по внутреннему индексу плоского массива."""

        return self._squares[index]

    def __iter__(self):
        """Итерирует по внутренним индексам клеток в порядке номеров полей."""

        return iter(self._board_map)

    def state(self, ndx: int) -> SquareState:
        """Состояние клетки по внутреннему индексу плоского массива."""
        return self._squares[ndx]

    def set_state(self, ndx: int, state: SquareState):
        """Устанавливает состояние клетки по внутреннему индексу.

        Метод обновляет не только плоский массив клеток, но и учёт фигур:
        клетка удаляется из обоих множеств и, если новое состояние
        соответствует фигуре, добавляется в множество её владельца.

        Args:
            ndx: Внутренний индекс клетки плоского массива.
            state: Новое состояние клетки.
        """

        self._squares[ndx] = state
        self._white_pieces.discard(ndx)
        self._black_pieces.discard(ndx)
        if state in (SquareState.WHITE_MAN, SquareState.WHITE_KING):
            self._white_pieces.add(ndx)
        elif state in (SquareState.BLACK_MAN, SquareState.BLACK_KING):
            self._black_pieces.add(ndx)

    def number_at(self, ndx: int) -> int:
        """Обратное отображение: внутренний индекс -> номер игрового поля (1..N)."""
        return self._number_map[ndx]

    def ndx_of_number(self, number: int) -> int:
        """Прямое отображение: номер игрового поля (1..N) -> внутренний индекс."""
        return self._board_map[number - 1]

    def clear(self):
        """Сбрасывает доску к начальной расстановке и очищает учёт фигур."""

        self._board_init(self._board_size, self._squares, self._board_map)
        self._rebuild_number_map()
        self._white_pieces.clear()
        self._black_pieces.clear()

    def remove_piece(self, square_ndx: int):
        """Удаляет фигуру с клетки по номеру игрового поля (1..N).

        Args:
            square_ndx: Номер игрового поля, с которого снимается фигура.
        """

        ndx = self._board_map[square_ndx - 1]
        self._squares[ndx] = SquareState.EMPTY
        if ndx in self._white_pieces:
            self._white_pieces.remove(ndx)
        else:
            self._black_pieces.remove(ndx)

    def set_piece(self, piece: Piece):
        """Устанавливает фигуру на доску по номеру её игрового поля.

        Args:
            piece: Фигура, содержащая номер поля, состояние клетки и владельца.
        """

        ndx = self._board_map[piece.square_ndx - 1]
        self._squares[ndx] = piece.square_state
        if piece.owner == Player.WHITE:
            self._white_pieces.add(ndx)
        else:
            self._black_pieces.add(ndx)

    def setup(self, position: str):
        """Устанавливает позицию по строке FEN (PDN).

        Текущее состояние доски предварительно сбрасывается.

        Args:
            position: Строка позиции в формате FEN (PDN).
        """
        fen = Fen()
        self.clear()
        fen.parse(position)
        for piece in fen.pieces:
            self.set_piece(piece)
        self._player_to_move = fen.player_to_move

    def to_fen(self, start_color: Player = Player.WHITE) -> str:
        """Возвращает текущую позицию в формате FEN (PDN).

        Формат: <цвет хода>:W<номера белых>:B<номера чёрных>,
        дамки помечаются префиксом "K". Номера в каждой секции
        отсортированы по возрастанию.
        """
        return fen_from_states(
            dict(enumerate(self._squares)), self.number_at, start_color
        )

    @property
    def player_to_move(self):
        """Игрок, чья очередь хода."""
        return self._player_to_move

    @player_to_move.setter
    def player_to_move(self, player: Player):
        """Устанавливает игрока, чья очередь хода."""
        self._player_to_move = player

    @property
    def height(self) -> int:
        """Высота доски в клетках."""
        return self._board_size.height

    @property
    def width(self) -> int:
        """Ширина доски в клетках."""
        return self._board_size.width

    @property
    def white_pieces(self) -> set[int]:
        """Номера полей (1..N), занятых белыми фигурами."""
        return {self._number_map[ndx] for ndx in self._white_pieces}

    @property
    def black_pieces(self) -> set[int]:
        """Номера полей (1..N), занятых чёрными фигурами."""
        return {self._number_map[ndx] for ndx in self._black_pieces}
