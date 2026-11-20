from pythia.core.board_size import BoardSize
from pythia.core.game_type import GameType
from pythia.damboard.damboard import DamBoard

INTERNATIONAL_START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
)

RUSSIAN_START_FEN = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"
BRAZILIAN_START_FEN = (
    "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"
)


class Engine:
    def __init__(self, game_type: GameType = GameType.INTERNATIONAL):
        self._game_type = game_type
        self._board: DamBoard = self._create_board(game_type)
        self._init_board(game_type)

    def _create_board(self, game_type: GameType) -> DamBoard:
        if game_type == GameType.INTERNATIONAL:
            return DamBoard(BoardSize.BIG)
        elif game_type == GameType.RUSSIAN or game_type == GameType.BRAZILIAN:
            return DamBoard(BoardSize.STANDARD)

    def _init_board(self, game_type: GameType):
        if game_type == GameType.INTERNATIONAL:
            self._board.setup(INTERNATIONAL_START_FEN)
        elif game_type == GameType.RUSSIAN:
            self._board.setup(RUSSIAN_START_FEN)
        elif game_type == GameType.BRAZILIAN:
            self._board.setup(BRAZILIAN_START_FEN)
        else:
            raise ValueError("Invalid game type")

    @property
    def board(self) -> DamBoard:
        return self._board
