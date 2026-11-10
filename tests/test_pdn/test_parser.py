"""Тесты чтения партий из PDN — см. pythia.pdn.parser.

Основной сценарий — файл parser_pdn_international.pdn в корне проекта:
одна партия в международные шашки, 62 номера ходов (124 полухода).
Позиции проверяются через повторный разбор FEN: начальная позиция —
стартовая расстановка, финальная — две чёрные дамки на 23 и 47 без
белых фигур.
"""

from pathlib import Path

import pytest

from pythia.core.rank import Rank
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.pdn.fen import Fen
from pythia.pdn.parser import STANDARD_START_FEN, PdnParser

SAMPLE_FILE = Path(__file__).parents[2] / "parser_pdn_international.pdn"


@pytest.fixture
def sample_game():
    (game,) = PdnParser().parse_file(str(SAMPLE_FILE))
    return game


def test_sample_file_contains_one_game(sample_game):
    assert len(PdnParser().parse_file(str(SAMPLE_FILE))) == 1


def test_headers_are_read(sample_game):
    headers = sample_game.headers
    assert headers["Event"] == "Rated Bullet game"
    assert headers["Site"] == "https://lidraughts.org/pMVV4F7R"
    assert headers["Date"] == "2025.02.12"
    assert headers["White"] == "fred"
    assert headers["Black"] == "A1621"
    assert headers["Result"] == "0-2"
    assert headers["GameType"] == "20"
    assert headers["TimeControl"] == "60+1"
    assert headers["Termination"] == "Normal"


def test_first_position_is_standard_start(sample_game):
    # to_fen не ставит завершающую точку, поэтому сравнение без неё.
    assert sample_game.positions[0] == STANDARD_START_FEN.rstrip(".")


def test_position_after_each_half_move(sample_game):
    # 62 номера ходов -> 124 полухода -> 125 позиций (включая начальную).
    assert len(sample_game.positions) == 124 + 1


def test_positions_are_chained(sample_game):
    # Каждая следующая позиция получена из предыдущей одним полуходом:
    # в FEN меняется цвет хода и/или расстановка фигур.
    positions = sample_game.positions
    assert all(
        current != previous for previous, current in zip(positions, positions[1:], strict=False)
    )


def test_final_position_two_black_kings(sample_game):
    final = sample_game.positions[-1]
    board = Damboard(BoardSize.BIG)
    board.setup(final)
    assert board.white_pieces == set()
    assert board.black_pieces == {23, 47}

    fen = Fen()
    fen.parse(final)
    assert {piece.rank for piece in fen.pieces} == {Rank.KING}


def test_synthetic_game_with_capture_and_result_token():
    # Ход взятием из начала той же партии: 33-28 19-23 28x19 14x23.
    # Токен результата "*" не должен попадать в список ходов.
    text = '[Event "Test"]\n[Result "*"]\n\n1. 33-28 19-23 2. 28x19 14x23 *\n'
    (game,) = PdnParser().parse(text)
    assert game.headers["Result"] == "*"
    assert len(game.positions) == 5

    board = Damboard(BoardSize.BIG)
    board.setup(game.positions[-1])
    # Белая простая 33->28->19 побита чёрной, чёрная простая ушла 14->23,
    # побив белую простую 19.
    assert board.white_pieces == set(range(31, 51)) - {33}
    assert board.black_pieces == set(range(1, 21)) - {14, 19} | {23}


def test_multiple_games_in_one_text():
    text = (
        '[White "A"]\n'
        '[Result "1-1"]\n'
        "\n"
        "1. 32-28 19-23\n"
        "\n"
        '[White "B"]\n'
        '[Result "2-0"]\n'
        "\n"
        "1. 33-28 18-22\n"
    )
    games = PdnParser().parse(text)
    assert [game.headers["White"] for game in games] == ["A", "B"]
    assert all(len(game.positions) == 3 for game in games)
    # Результат не должен быть ошибочно разобран как ход.
    assert all(game.positions[-1].startswith(("W", "B")) for game in games)


def test_unrecognized_token_raises():
    with pytest.raises(ValueError, match="Нераспознанный токен хода"):
        PdnParser().parse('[White "A"]\n1. zz-28\n')


def test_illegal_move_raises():
    # 32-28x25 — цепочка взятия, которой нет в стартовой позиции.
    with pytest.raises(ValueError, match="не определён однозначно"):
        PdnParser().parse('[White "A"]\n1. 32-28 19-23 2. 28x25\n')
