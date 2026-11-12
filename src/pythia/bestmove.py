import re

from pythia.core.piece import Piece
from pythia.core.player import Player
from pythia.core.rank import Rank
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.rules import INTERNATIONAL, Rules

START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20."
)

MOVE_TOKEN_RE = re.compile(r"\d+(?:[xX:\-]\d+)+[!?]*")

print("I'm testing best move module . . .")

str_move = "35-30"
if not MOVE_TOKEN_RE.fullmatch(str_move):
    raise ValueError(f"Нераспознанный токен хода: {str_move!r}")
path = tuple(int(number) for number in re.findall(r"\d+", str_move))
print(path)

board = Damboard(BoardSize.BIG)
board.setup(START_FEN)
generator = MoveGenerator(board, INTERNATIONAL)

canditates = generator.generate(Player.WHITE)
for candidate in canditates:
    if candidate.path == path:
        print(f"Move found from {candidate.path[0]} to {candidate.path[-1]}")
        board.remove_piece(candidate.path[0])
        
    print(candidate.path)

    



