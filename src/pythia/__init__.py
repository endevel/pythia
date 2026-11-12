from datetime import datetime

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.movegen.perft import generator_from_fen, perft
from pythia.movegen.rules import INTERNATIONAL

START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20."
)


def run_perft_international_7():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    print(
        f"time: {datetime.now().time()} perft at depth 7: {perft(generator, Player.WHITE, 7)}"
    )


def run_perft_international_8():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    print(
        f"time: {datetime.now().time()} perft at depth 8: {perft(generator, Player.WHITE, 8)}"
    )


def run_perft_international_9():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    print(
        f"time: {datetime.now().time()} perft at depth 9: {perft(generator, Player.WHITE, 9)}"
    )


def run_perft_international_10():
    generator = generator_from_fen(START_FEN, INTERNATIONAL, BoardSize.BIG)
    print(
        f"time: {datetime.now().time()} perft at depth 10: {perft(generator, Player.WHITE, 10)}"
    )


def main() -> None:
    print("Hello from pythia!")
    print(f"time: {datetime.now().time()} Start calculate perft")
    run_perft_international_7()
    run_perft_international_8()
    run_perft_international_9()
    run_perft_international_10()
