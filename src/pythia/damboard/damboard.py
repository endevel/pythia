from collections.abc import Callable

from pythia.core.square_state import SquareState
from pythia.damboard.board_size import BoardSize
from pythia.damboard.square_builders.standard_builder import build_standard_board


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
        board_init(self.__board_size, self.__squares, self.__board_map)

    def __getitem__(self, index):
        return self.__squares[index]

    def __iter__(self):
        return iter(self.__board_map)

    @property
    def height(self) -> int:
        return self.__board_size.height

    @property
    def width(self) -> int:
        return self.__board_size.width
