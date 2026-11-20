import pytest

from pythia.core.board_size import BoardSize
from pythia.core.rules import Rules
from pythia.pdn.parser import PdnParser

RUSSIAN_START = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"

INTERNATIONAL_START = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
)


def russian_parser() -> PdnParser:
    return PdnParser(rules=Rules.RUSSIAN, board_size=BoardSize.STANDARD)


def test_parse_headers_and_replays_moves():
    text = """
[Event "Test"]
[White "Alice"]
[Black "Bob"]
[Result "0-1"]

1. 22-18 9-13 0-1
"""

    games = russian_parser().parse(text)

    assert len(games) == 1
    game = games[0]
    assert game.headers == {
        "Event": "Test",
        "White": "Alice",
        "Black": "Bob",
        "Result": "0-1",
    }
    assert game.positions == [
        RUSSIAN_START,
        "B:W18,21,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12",
        "W:W18,21,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,10,11,12,13",
    ]


def test_parse_uses_international_start_by_default():
    text = """
[Event "International"]

1. 32-28
"""

    games = PdnParser().parse(text)

    assert games[0].positions == [
        INTERNATIONAL_START,
        (
            "B:W28,31,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
            "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
        ),
    ]


def test_parse_uses_fen_header_and_white_capture():
    text = """
[FEN "W:W22:B18"]

1. 22x15
"""

    games = russian_parser().parse(text)

    assert games[0].positions == ["W:W22:B18", "B:W15:B"]


def test_parse_respects_black_to_move_from_fen():
    text = """
[FEN "B:W21:B1"]

1. 1-5
"""

    games = russian_parser().parse(text)

    assert games[0].positions == ["B:W21:B1", "W:W21:B5"]


@pytest.mark.parametrize("notation", ["21x14x3", "21x3"])
def test_parse_matches_full_and_short_capture_notation(notation):
    text = f"""
[FEN "W:WK21:B10,17"]

1. {notation}
"""

    games = russian_parser().parse(text)

    assert games[0].positions == ["W:WK21:B10,17", "B:WK3:B"]


def test_parse_ignores_comments_variations_and_result():
    text = """
[White "Alice"]

1. 22-18 {block comment} 9-13 ; line comment
2. 21-17 (2... 10-14) 1/2-1/2
"""

    games = russian_parser().parse(text)

    assert len(games[0].positions) == 4


def test_parse_splits_games_after_movetext():
    text = """
[White "Alice"]

1. 22-18 9-13

[White "Bob"]

1. 23-18 10-14
"""

    games = russian_parser().parse(text)

    assert [game.headers["White"] for game in games] == ["Alice", "Bob"]
    assert all(len(game.positions) == 3 for game in games)


def test_parse_headers_without_movetext_gives_start_position():
    text = """
[Event "Empty"]
[White "Alice"]
"""

    games = russian_parser().parse(text)

    assert len(games) == 1
    assert games[0].headers == {"Event": "Empty", "White": "Alice"}
    assert games[0].positions == [RUSSIAN_START]


def test_parse_empty_text_gives_no_games():
    assert russian_parser().parse("") == []


def test_parse_raises_for_unrecognized_move_token():
    with pytest.raises(ValueError, match="Нераспознанный токен хода"):
        russian_parser().parse('[White "Alice"]\n\n1. 22=18')


def test_parse_raises_for_illegal_move():
    with pytest.raises(ValueError, match="не определён однозначно"):
        russian_parser().parse('[White "Alice"]\n\n1. 22-16')


def test_parse_file_reads_all_games(tmp_path):
    path = tmp_path / "games.pdn"
    path.write_text(
        """
[White "Alice"]

1. 22-18 9-13

[White "Bob"]

1. 23-18 10-14
""",
        encoding="utf-8",
    )

    games = russian_parser().parse_file(str(path))

    assert [game.headers["White"] for game in games] == ["Alice", "Bob"]


@pytest.mark.parametrize(
    "text",
    [
        "",
        '[Event "Empty"]\n[White "Alice"]',
        '[White "Alice"]\n\n1. 22-18 9-13',
        '[White "Alice"]\n\n1. 22-18 9-13\n\n[White "Bob"]\n\n1. 23-18 10-14',
        "1. 22-18 9-13",
        '1. 22-18\n\n[White "Bob"]',
    ],
)
def test_count_games_matches_parse(text):
    parser = russian_parser()

    assert parser.count_games(text) == len(parser.parse(text))


def test_count_games_file_counts_without_replay(tmp_path):
    path = tmp_path / "games.pdn"
    path.write_text(
        """
[White "Alice"]

1. 22-18 9-13

[White "Bob"]

1. 23-18 10-14
""",
        encoding="utf-8",
    )

    assert russian_parser().count_games_file(str(path)) == 2


def test_parse_file_reports_progress(tmp_path):
    path = tmp_path / "games.pdn"
    path.write_text(
        """
[White "Alice"]

1. 22-18 9-13

[White "Bob"]

1. 23-18 10-14
""",
        encoding="utf-8",
    )

    progress: list[tuple[int, int]] = []
    games = russian_parser().parse_file(
        str(path),
        progress=lambda done, total: progress.append((done, total)),
    )

    assert len(games) == 2
    assert progress == [(1, 2), (2, 2)]


def test_iter_parse_file_yields_games(tmp_path):
    path = tmp_path / "games.pdn"
    path.write_text(
        """
[White "Alice"]

1. 22-18 9-13

[White "Bob"]

1. 23-18 10-14
""",
        encoding="utf-8",
    )

    games = list(russian_parser().iter_parse_file(str(path)))

    assert [game.headers["White"] for game in games] == ["Alice", "Bob"]
