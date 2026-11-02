from pythia.core import SquareState
from pythia.damboard.board_size import BoardSize


def build_standard_board(board_size: BoardSize, squares: list[SquareState], board_map: list[int]):
    board_map.clear()
    squares.clear()
    ndx = 0
    for row in range(board_size.height + 2):
        for col in range(board_size.width + 2):
            if row == 0 or row == board_size.height + 1:
                squares.append(SquareState.OUT_OF_BOARD)
            elif col == 0 or col == board_size.width + 1:
                squares.append(SquareState.OUT_OF_BOARD)
            else:
                if (row + col) % 2 == 1:
                    squares.append(SquareState.EMPTY)
                    board_map.append(ndx)
                else:
                    squares.append(SquareState.OUT_OF_BOARD)
            ndx += 1
