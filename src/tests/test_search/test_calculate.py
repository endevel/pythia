import pytest

from pythia.damboard.damboard import DamBoard
from pythia.evaluation.russian_evaluation import RussianEvaluation
from pythia.movegen.russian_move_gen import RussianMoveGen
from pythia.search.search_best_move import SearchBestMove, SearchTimeout


def make_board(position: str) -> DamBoard:
    board = DamBoard()
    board.setup(position)
    return board


def make_search(board: DamBoard) -> SearchBestMove:
    return SearchBestMove(
        RussianMoveGen(board, board.player_to_move),
        RussianEvaluation(),
    )


class DepthRecordingSearch(SearchBestMove):
    """Поиск, который запоминает глубины и прерывается на третьей."""

    def __init__(self, board: DamBoard):
        super().__init__(
            RussianMoveGen(board, board.player_to_move),
            RussianEvaluation(),
        )
        self.depths: list[int] = []

    def search_best_move(self, board, depth=3, deadline=None):
        self.depths.append(depth)
        if depth == 3:
            raise SearchTimeout
        return super().search_best_move(board, depth, deadline=deadline)


class DeadlineRecordingSearch(SearchBestMove):
    """Поиск, который запоминает дедлайн и сразу прерывается."""

    def __init__(self, board: DamBoard):
        super().__init__(
            RussianMoveGen(board, board.player_to_move),
            RussianEvaluation(),
        )
        self.deadlines: list[float | None] = []

    def search_best_move(self, board, depth=3, deadline=None):
        self.deadlines.append(deadline)
        raise SearchTimeout


class InterruptingSearch(SearchBestMove):
    """Поиск, прерывающийся внутри negamax на третьем узле."""

    def __init__(self, board: DamBoard):
        super().__init__(
            RussianMoveGen(board, board.player_to_move),
            RussianEvaluation(),
        )
        self.calls = 0

    def _negamax(
        self,
        board,
        depth,
        alpha,
        beta,
        ply,
        deadline=None,
    ):
        self.calls += 1
        if self.calls == 3:
            raise SearchTimeout
        return super()._negamax(board, depth, alpha, beta, ply, deadline)


def test_calculate_returns_legal_move():
    board = make_board("W:W22:B18")

    move = make_search(board).calculate(board, time_limit=0.05)

    assert move is not None
    assert board.number_at(move.from_square) == 22
    assert board.number_at(move.to_square) == 15
    assert [board.number_at(ndx) for ndx, _ in move.taken] == [18]


def test_calculate_returns_none_when_no_moves_available():
    board = make_board("B:W22:B")

    assert make_search(board).calculate(board, time_limit=0.05) is None


def test_calculate_restores_board():
    board = make_board("W:W9,10,11,12:B21,22,23,24")
    fen_before = board.to_fen(board.player_to_move)

    make_search(board).calculate(board, time_limit=0.05)

    assert board.to_fen(board.player_to_move) == fen_before


@pytest.mark.parametrize(
    "time_limit",
    [0, -1, float("inf"), float("nan")],
)
def test_calculate_rejects_invalid_time_limit(time_limit):
    board = make_board("W:W22:B18")

    with pytest.raises(ValueError):
        make_search(board).calculate(board, time_limit=time_limit)


def test_calculate_increases_depth_until_timeout():
    board = make_board("W:W22:B18")
    search = DepthRecordingSearch(board)

    search.calculate(board, time_limit=1.0)

    assert search.depths == [1, 2, 3]


def test_calculate_uses_75_percent_of_time_limit(monkeypatch):
    board = make_board("W:W22:B18")
    search = DeadlineRecordingSearch(board)
    monkeypatch.setattr(
        "pythia.search.search_best_move.time.monotonic",
        lambda: 100.0,
    )

    search.calculate(board, time_limit=2.0)

    assert search.deadlines == [101.5]


def test_search_best_move_restores_board_after_timeout():
    board = make_board("W:W9,10,11,12:B21,22,23,24")
    fen_before = board.to_fen(board.player_to_move)
    search = InterruptingSearch(board)

    with pytest.raises(SearchTimeout):
        search.search_best_move(board, depth=5)

    assert board.to_fen(board.player_to_move) == fen_before
