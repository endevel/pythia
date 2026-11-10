"""Чтение партий из файлов в формате PDN (Portable Draughts Notation).

PDN-файл состоит из партий. Каждая партия — блок заголовка (пары
`[Key "Value"]`, по одной на строке) и текст ходов (movetext), например:

    [Event "Rated Bullet game"]
    [White "fred"]
    [Result "0-2"]

    1. 34-29 18-22 2. 40-34 12-18 ... 0-2

Парсер разбирает заголовки и список полуходов, после чего «проигрывает»
партию на `MoveGenerator`: каждый ход из нотации сопоставляется с
корректным ходом, сгенерированным по правилам выбранного варианта игры
(по умолчанию — международные шашки). Так проверяется легальность
записанных ходов, а превращения в дамку и побитые фигуры вычисляются
движком, а не из нотации.

Результат по каждой партии — `PdnGame`: словарь заголовков и список
позиций в формате FEN/PDN. `positions[0]` — начальная расстановка,
`positions[i]` — позиция после i-го полухода.
"""

import re
from dataclasses import dataclass, field

from pythia.core.player import Player
from pythia.damboard.board_size import BoardSize
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.move import Move
from pythia.movegen.rules import INTERNATIONAL, Rules
from pythia.pdn.fen import Fen, fen_from_states

#: Начальная расстановка международных шашек (10x10, FMJD-нумерация):
#: белые 31-50, чёрные 1-20, первый ход у белых.
STANDARD_START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20."
)

#: Строка заголовка: `[Key "Value"]`.
HEADER_RE = re.compile(r'^\[(\w+)\s+"(.*)"\]$')

#: Результат партии (учитывается только как отдельный токен movetext).
RESULT_RE = re.compile(r"1/2-1/2|1-0|0-1|1-1|0-2|2-0|\*")

#: Номер хода с точками: `1.`, `12...` и т.п.
MOVE_NUMBER_RE = re.compile(r"^\d+\.+")

#: Токен полухода: цепочка номеров полей через `-` (тихий ход),
#: `x` или `:` (взятие), с необязательными знаками `!`/`?` в конце.
MOVE_TOKEN_RE = re.compile(r"\d+(?:[xX:\-]\d+)+[!?]*")


@dataclass
class PdnGame:
    """Партия, прочитанная из PDN.

    Attributes:
        headers: заголовок партии: имя тега -> значение (Event, White,
            Black, Result и т.д.).
        positions: позиции в формате FEN/PDN. `positions[0]` — начальная
            расстановка, `positions[i]` — позиция после i-го полухода;
            цвет хода в каждой позиции — сторона, делающая следующий ход.
    """

    headers: dict[str, str] = field(default_factory=dict)
    positions: list[str] = field(default_factory=list)


class PdnParser:
    """Читает партии из текста (или файла) в формате PDN."""

    def __init__(
        self,
        rules: Rules = INTERNATIONAL,
        board_size: BoardSize = BoardSize.BIG,
    ):
        """Аргументы:
        rules: правила варианта игры (влияют на легальность ходов при
            replay); по умолчанию — международные шашки.
        board_size: размер доски; по умолчанию — BIG (10x10).
        """
        self._rules = rules
        self._board_size = board_size

    def parse_file(self, path: str) -> list[PdnGame]:
        """Читает все партии из PDN-файла."""
        with open(path, encoding="utf-8") as file:
            return self.parse(file.read())

    def parse(self, text: str) -> list[PdnGame]:
        """Читает все партии из PDN-текста.

        Новая партия начинается, когда после movetext встречается строка
        заголовка; партия без movetext (только заголовок) получает в
        `positions` единственную начальную позицию.
        """
        games: list[PdnGame] = []
        headers: dict[str, str] = {}
        movetext: list[str] = []
        saw_movetext = False

        for raw_line in text.splitlines():
            line = raw_line.strip()
            header = HEADER_RE.match(line)
            if header:
                if saw_movetext:
                    games.append(self._build_game(headers, movetext))
                    headers, movetext, saw_movetext = {}, [], False
                headers[header.group(1)] = header.group(2)
            elif line:
                saw_movetext = True
                movetext.append(line)

        if headers or movetext:
            games.append(self._build_game(headers, movetext))
        return games

    def _build_game(self, headers: dict[str, str], movetext: list[str]) -> PdnGame:
        positions = self._replay(headers, movetext)
        return PdnGame(headers=dict(headers), positions=positions)

    def _replay(self, headers: dict[str, str], movetext: list[str]) -> list[str]:
        """Проигрывает партию и возвращает позиции после каждого полухода."""
        board = Damboard(self._board_size)
        fen_header = headers.get("FEN")
        if fen_header:
            board.setup(fen_header)
            fen = Fen()
            fen.parse(fen_header)
            player = fen.start_color
        else:
            board.setup(STANDARD_START_FEN)
            player = Player.WHITE

        generator = MoveGenerator(board, self._rules)
        positions = [board.to_fen(player)]

        for notation, is_capture in self._move_notations(movetext):
            move = self._match_move(generator, player, notation, is_capture)
            generator.make_move(move, player)
            player = Player.BLACK if player == Player.WHITE else Player.WHITE
            positions.append(fen_from_states(generator.states, board.number_at, player))
        return positions

    @staticmethod
    def _move_notations(movetext: list[str]) -> list[tuple[tuple[int, ...], bool]]:
        """Разбирает movetext в список полуходов.

        Возвращает пары (номера полей хода, признак взятия). Номер хода
        (`1.`), результаты (`1-0`, `0-2`, `*`), комментарии (`{...}`,
        `; ...`) и варианты (`(...)`) отбрасываются.
        """
        text = "\n".join(re.sub(r";.*", " ", line) for line in movetext)
        text = re.sub(r"\{[^}]*\}", " ", text)
        text = re.sub(r"\([^)]*\)", " ", text)

        notations: list[tuple[tuple[int, ...], bool]] = []
        for token in text.split():
            token = MOVE_NUMBER_RE.sub("", token).strip("!?")
            if not token or RESULT_RE.fullmatch(token):
                continue
            if not MOVE_TOKEN_RE.fullmatch(token):
                raise ValueError(f"Нераспознанный токен хода: {token!r}")
            is_capture = "x" in token.lower() or ":" in token
            path = tuple(int(number) for number in re.findall(r"\d+", token))
            notations.append((path, is_capture))
        return notations

    def _match_move(
        self,
        generator: MoveGenerator,
        player: Player,
        notation: tuple[int, ...],
        is_capture: bool,
    ) -> Move:
        """Сопоставляет ход из нотации с легальным ходом генератора.

        Нотация взятия может не содержать промежуточных полей приземления
        (`39x19` вместо `39x28x19`), поэтому сначала ищется точное
        совпадение пути, затем — совпадение по крайним полям.
        """
        candidates = generator.generate(player)
        candidates = [m for m in candidates if m.is_capture == is_capture]

        exact = [m for m in candidates if m.path == notation]
        if exact:
            candidates = exact
        else:
            candidates = [
                m for m in candidates if m.path[0] == notation[0] and m.path[-1] == notation[-1]
            ]

        if len(candidates) != 1:
            raise ValueError(
                f"Ход {'-'.join(map(str, notation))} игрока {player.name} "
                f"не определён однозначно (совпадений: {len(candidates)})"
            )
        return candidates[0]
