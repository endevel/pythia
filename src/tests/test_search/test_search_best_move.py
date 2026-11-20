import pytest

from pythia.damboard.damboard import DamBoard
from pythia.evaluation.russian_evaluation import RussianEvaluation
from pythia.movegen.russian_move_gen import RussianMoveGen
from pythia.search.search_best_move import SearchBestMove


def make_board(position: str) -> DamBoard:
    board = DamBoard()
    board.setup(position)
    return board


def make_search(board: DamBoard) -> SearchBestMove:
    return SearchBestMove(
        RussianMoveGen(board, board.player_to_move),
        RussianEvaluation(),
    )


def test_returns_none_when_no_moves_available():
    board = make_board("B:W22:B")

    assert make_search(board).search_best_move(board) is None


def test_depth_must_be_positive():
    board = make_board("W:W22:B")

    with pytest.raises(ValueError):
        make_search(board).search_best_move(board, depth=0)


def test_chooses_mandatory_capture():
    board = make_board("W:W22:B18")

    move = make_search(board).search_best_move(board, depth=1)

    assert move is not None
    assert board.number_at(move.from_square) == 22
    assert board.number_at(move.to_square) == 15
    assert [board.number_at(ndx) for ndx, _ in move.taken] == [18]


def test_chooses_capture_with_best_material_result():
    # Шашка 22 снимает две фигуры (18 и 10), шашка 28 — только одну (24).
    board = make_board("W:W22,28:B18,10,24")

    move = make_search(board).search_best_move(board, depth=1)

    assert move is not None
    assert board.number_at(move.from_square) == 22
    assert board.number_at(move.to_square) == 6
    assert [board.number_at(ndx) for ndx, _ in move.taken] == [18, 10]


def test_black_chooses_capture_with_best_material_result():
    board = make_board("B:B22,28:W18,10,24")

    move = make_search(board).search_best_move(board, depth=1)

    assert move is not None
    assert board.number_at(move.from_square) == 22
    assert [board.number_at(ndx) for ndx, _ in move.taken] == [18, 10]


def test_board_is_restored_after_search():
    board = make_board("W:W22,28:B18,10,24")
    fen_before = board.to_fen(board.player_to_move)

    make_search(board).search_best_move(board, depth=2)

    assert board.to_fen(board.player_to_move) == fen_before


def test_accepts_move_generator_class():
    board = make_board("W:W22:B18")
    search = SearchBestMove(RussianMoveGen, RussianEvaluation())

    move = search.search_best_move(board, depth=1)

    assert move is not None
    assert board.number_at(move.from_square) == 22
