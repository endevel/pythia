from pythia.core.player import Player
from pythia.damboard.damboard import Damboard


def test_to_fen_start_position():
    board = Damboard()
    board.setup("W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12.")
    assert board.to_fen() == "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"


def test_to_fen_with_kings():
    board = Damboard()
    board.setup("B:WK1,25,27,32:BK30,19,21,23.")
    assert board.to_fen(Player.BLACK) == "B:WK1,25,27,32:B19,21,23,K30"


def test_to_fen_numbers_sorted_numerically():
    # Номера должны сортироваться по значению, а не по строке (2 < 10).
    board = Damboard()
    board.setup("W:W32,2,10:B5.")
    assert board.to_fen() == "W:W2,10,32:B5"


def test_setup_to_fen_roundtrip():
    # Префикс "K" в парсере применяется к отдельному токену,
    # поэтому в секциях явно помечаем каждую дамку.
    position = "W:W19,K26,30,32:BK18,K20,K22,K25,K27,K29,K31."
    board = Damboard()
    board.setup(position)
    fen = board.to_fen()
    assert fen == "W:W19,K26,30,32:BK18,K20,K22,K25,K27,K29,K31"
    restored = Damboard()
    restored.setup(fen)
    assert restored.white_pieces == board.white_pieces
    assert restored.black_pieces == board.black_pieces
