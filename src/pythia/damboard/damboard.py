from collections.abc import Callable

from pythia.core.piece import Piece
from pythia.core.player import Player
from pythia.core.square_state import SquareState
from pythia.damboard.board_size import BoardSize
from pythia.damboard.square_builders.standard_builder import build_standard_board
from pythia.pdn.fen import Fen


class Damboard:
    def __init__(
        self,
        board_size: BoardSize = BoardSize.STANDARD,
        board_init: Callable[
            [BoardSize, list[SquareState], list[int]], None
        ] = build_standard_board,
    ):
        self.__board_size = board_size
        self.__squares = []
        self.__board_map = []
        self.__white_pieces = set()
        self.__black_pieces = set()
        self.__board_init = board_init
        board_init(self.__board_size, self.__squares, self.__board_map)

    def __getitem__(self, index):
        return self.__squares[index]

    def __iter__(self):
        return iter(self.__board_map)

    def clear(self):
        self.__board_init(self.__board_size, self.__squares, self.__board_map)

    def remove_piece(self, square_ndx: int):
        ndx = self.__board_map[square_ndx - 1]
        self.__squares[ndx] = SquareState.EMPTY
        if ndx in self.__white_pieces:
            self.__white_pieces.remove(ndx)
        else:
            self.__black_pieces.remove(ndx)

    def set_piece(self, piece: Piece):
        ndx = self.__board_map[piece.square_ndx - 1]
        self.__squares[ndx] = piece.square_state
        if piece.owner == Player.WHITE:
            self.__white_pieces.add(ndx)
        else:
            self.__black_pieces.add(ndx)

    def setup(self, position: str):
        fen = Fen()
        self.clear()
        fen.parse(position)
        for piece in fen.pieces:
            self.set_piece(piece)

    @property
    def height(self) -> int:
        return self.__board_size.height

    @property
    def width(self) -> int:
        return self.__board_size.width

    @property
    def white_pieces(self) -> set[int]:
        return self.__white_pieces

    @property
    def black_pieces(self) -> set[int]:
        return self.__black_pieces
