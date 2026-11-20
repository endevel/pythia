"""Чтение партий из файлов в формате PDN (Portable Draughts Notation).

PDN-файл состоит из партий. Каждая партия — блок заголовка (пары
`[Key "Value"]`, по одной на строке) и текст ходов (movetext), например:

    [Event "Rated Bullet game"]
    [White "fred"]
    [Result "0-2"]

    1. 32-28 19-23 2. 37-32 14-19 ... 0-2

Парсер разбирает заголовки и список полуходов, после чего «проигрывает»
партию на генераторе ходов: каждый ход из нотации сопоставляется с
корректным ходом, сгенерированным по правилам выбранного варианта игры
(по умолчанию — международные шашки). Так проверяется легальность
записанных ходов, а превращения в дамку и побитые фигуры вычисляются
движком, а не из нотации.

Результат по каждой партии — `PdnGame`: словарь заголовков и список
позиций в формате FEN/PDN. `positions[0]` — начальная расстановка,
`positions[i]` — позиция после i-го полухода.
"""

import re
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass, field

from pythia.core.board_size import BoardSize
from pythia.core.move import Move
from pythia.core.player import Player
from pythia.core.rules import Rules
from pythia.damboard.damboard import DamBoard
from pythia.movegen.base import GenerateMoveList
from pythia.movegen.international_move_gen import InternationalMoveGen
from pythia.movegen.russian_move_gen import RussianMoveGen
from pythia.search.move_func import do_move

#: Начальная расстановка международных шашек (10x10, FMJD-нумерация):
#: белые 31-50, чёрные 1-20, первый ход у белых.
STANDARD_START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
)

#: Начальная расстановка русских шашек (8x8): белые 21-32, чёрные 1-12,
#: первый ход у белых.
RUSSIAN_START_FEN = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"

#: Строка заголовка: `[Key "Value"]`.
HEADER_RE = re.compile(r'^\[(\w+)\s+"(.*)"\]$')

#: Результат партии (учитывается только как отдельный токен movetext).
RESULT_RE = re.compile(r"1/2-1/2|1-0|0-1|1-1|0-2|2-0|\*")

#: Номер хода с точками: `1.`, `12...` и т.п.
MOVE_NUMBER_RE = re.compile(r"^\d+\.+")

#: Токен полухода: цепочка номеров полей через `-` (тихий ход),
#: `x` или `:` (взятие), с необязательными знаками `!`/`?` в конце.
MOVE_TOKEN_RE = re.compile(r"\d+(?:[xX:\-]\d+)+[!?]*")

#: Колбэк прогресса разбора: ``(обработано партий, всего партий)``.
ProgressCallback = Callable[[int, int], None]


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
        rules: Rules = Rules.INTERNATIONAL,
        board_size: BoardSize | None = None,
    ):
        """Аргументы:
        rules: правила варианта игры (влияют на легальность ходов при
            replay); по умолчанию — международные шашки.
        board_size: размер доски; если не задан, выбирается по правилам:
            STANDARD (8x8) для русских шашек и BIG (10x10) для остальных.
        """
        self._rules = rules
        if board_size is None:
            board_size = BoardSize.STANDARD if rules is Rules.RUSSIAN else BoardSize.BIG
        self._board_size = board_size

    def count_games_file(self, path: str) -> int:
        """Быстро считает число партий в PDN-файле, не разбирая ходы.

        Выполняется за один проход по строкам без создания досок и
        генерации ходов, поэтому подходит для оценки объёма работы перед
        ``parse_file`` (например, для прогресс-бара).
        """
        with open(path, encoding="utf-8") as file:
            return self._count_games_in_lines(file)

    def count_games(self, text: str) -> int:
        """Быстро считает число партий в PDN-тексте, не разбирая ходы."""
        return self._count_games_in_lines(text.splitlines())

    @staticmethod
    def _count_games_in_lines(lines: Iterable[str]) -> int:
        """Считает партии по тому же правилу, что и ``_iter_parse_lines``.

        Новая партия начинается с заголовка после movetext; завершающая
        партия учитывается, если после последнего разделителя остались
        заголовки или movetext.
        """
        count = 0
        has_content = False
        saw_movetext = False

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue
            if HEADER_RE.match(line):
                if saw_movetext:
                    count += 1
                    saw_movetext = False
                has_content = True
            else:
                has_content = True
                saw_movetext = True

        return count + 1 if has_content else 0

    def parse_file(
        self,
        path: str,
        progress: ProgressCallback | None = None,
    ) -> list[PdnGame]:
        """Читает все партии из PDN-файла.

        Если передан ``progress``, файл сначала быстро сканируется для
        подсчёта партий, а затем каждая разобранная партия передаётся в
        колбэк как ``progress(обработано, всего)``. Это позволяет показывать
        прогресс-бар или процент выполнения на больших файлах.
        """
        if progress is None:
            return list(self.iter_parse_file(path))

        total = self.count_games_file(path)
        games: list[PdnGame] = []
        for game in self.iter_parse_file(path):
            games.append(game)
            progress(len(games), total)
        return games

    def iter_parse_file(self, path: str) -> Iterator[PdnGame]:
        """Лениво читает партии из файла, не загружая его целиком в память."""
        with open(path, encoding="utf-8") as file:
            yield from self._iter_parse_lines(file)

    def parse(
        self,
        text: str,
        progress: ProgressCallback | None = None,
    ) -> list[PdnGame]:
        """Читает все партии из PDN-текста.

        Новая партия начинается, когда после movetext встречается строка
        заголовка; партия без movetext (только заголовок) получает в
        `positions` единственную начальную позицию.

        ``progress`` работает так же, как в ``parse_file``.
        """

        if progress is None:
            return list(self._iter_parse_lines(text.splitlines()))

        total = self.count_games(text)
        games: list[PdnGame] = []
        for game in self._iter_parse_lines(text.splitlines()):
            games.append(game)
            progress(len(games), total)
        return games

    def _iter_parse_lines(self, lines: Iterable[str]) -> Iterator[PdnGame]:
        """Разбирает партии построчно, отдавая их по мере готовности."""
        headers: dict[str, str] = {}
        movetext: list[str] = []
        saw_movetext = False

        for raw_line in lines:
            line = raw_line.strip()
            header = HEADER_RE.match(line)
            if header:
                if saw_movetext:
                    yield self._build_game(headers, movetext)
                    headers, movetext, saw_movetext = {}, [], False
                headers[header.group(1)] = header.group(2)
            elif line:
                saw_movetext = True
                movetext.append(line)

        if headers or movetext:
            yield self._build_game(headers, movetext)

    def _build_game(self, headers: dict[str, str], movetext: list[str]) -> PdnGame:
        positions = self._replay(headers, movetext)
        return PdnGame(headers=dict(headers), positions=positions)

    def _start_fen(self) -> str:
        """Возвращает начальную расстановку для выбранного размера доски."""
        if self._board_size is BoardSize.STANDARD:
            return RUSSIAN_START_FEN
        return STANDARD_START_FEN

    def _replay(self, headers: dict[str, str], movetext: list[str]) -> list[str]:
        """Проигрывает партию и возвращает позиции после каждого полухода."""
        board = DamBoard(self._board_size)
        board.setup(headers.get("FEN") or self._start_fen())
        player = board.player_to_move
        positions = [board.to_fen(player)]

        for notation, is_capture in self._move_notations(movetext):
            move = self._match_move(board, player, notation, is_capture)
            do_move(board, move)
            player = board.player_to_move
            positions.append(board.to_fen(player))
        return positions

    @staticmethod
    def _strip_annotations(text: str) -> str:
        """Удаляет комментарии и варианты из movetext.

        Поддерживаются блочные комментарии ``{...}``, строчные ``; ...`` и
        варианты ``(...)``. В отличие от простых регулярных выражений
        сканер корректно обрабатывает вложенные скобки.
        """

        result: list[str] = []
        brace_depth = 0
        paren_depth = 0
        in_line_comment = False

        for char in text:
            if in_line_comment:
                if char == "\n":
                    in_line_comment = False
                    result.append(char)
                continue
            if brace_depth:
                if char == "{":
                    brace_depth += 1
                elif char == "}":
                    brace_depth -= 1
                continue
            if paren_depth:
                if char == "(":
                    paren_depth += 1
                elif char == ")":
                    paren_depth -= 1
                continue
            if char == "{":
                brace_depth = 1
            elif char == ";":
                in_line_comment = True
            elif char == "(":
                paren_depth = 1
            else:
                result.append(char)

        return "".join(result)

    @staticmethod
    def _move_notations(movetext: list[str]) -> list[tuple[tuple[int, ...], bool]]:
        """Разбирает movetext в список полуходов.

        Возвращает пары (номера полей хода, признак взятия). Номер хода
        (`1.`), результаты (`1-0`, `0-2`, `*`), комментарии (`{...}`,
        `; ...`) и варианты (`(...)`) отбрасываются.
        """
        text = PdnParser._strip_annotations("\n".join(movetext))

        notations: list[tuple[tuple[int, ...], bool]] = []
        for token in text.split():
            token = MOVE_NUMBER_RE.sub("", token).strip("!?")
            if not token or RESULT_RE.fullmatch(token):
                continue
            # Отдельный токен «...» (ход чёрных без номера) не является
            # ходом и должен быть пропущен, как и номер хода.
            if not token.strip("."):
                continue
            if not MOVE_TOKEN_RE.fullmatch(token):
                raise ValueError(f"Нераспознанный токен хода: {token!r}")
            is_capture = "x" in token.lower() or ":" in token
            path = tuple(int(number) for number in re.findall(r"\d+", token))
            notations.append((path, is_capture))
        return notations

    def _create_generator(self, board: DamBoard, player: Player) -> GenerateMoveList:
        """Создаёт генератор ходов для игрока по выбранным правилам."""
        if self._rules is Rules.INTERNATIONAL:
            return InternationalMoveGen(board, player)
        if self._rules is Rules.RUSSIAN:
            return RussianMoveGen(board, player)
        raise ValueError(f"Правила {self._rules.name} не поддерживаются PDN-парсером")

    @staticmethod
    def _notation_path(board: DamBoard, notation: tuple[int, ...]) -> tuple[int, ...]:
        """Переводит номера полей нотации во внутренние индексы доски."""
        if any(number < 1 for number in notation):
            raise ValueError(f"Недопустимый номер поля в ходе: {notation}")
        try:
            return tuple(board.ndx_of_number(number) for number in notation)
        except IndexError as error:
            raise ValueError(
                f"Номер поля вне доски {board.width}x{board.height}: {notation}"
            ) from error

    def _match_move(
        self,
        board: DamBoard,
        player: Player,
        notation: tuple[int, ...],
        is_capture: bool,
    ) -> Move:
        """Сопоставляет ход из нотации с легальным ходом генератора.

        Нотация взятия может не содержать промежуточных полей приземления
        (`39x19` вместо `39x28x19`), поэтому сначала ищется точное
        совпадение пути, затем — совпадение по крайним полям.
        """
        generator = self._create_generator(board, player)
        candidates = [
            move
            for move in generator.generate_move_list()
            if bool(move.taken) == is_capture
        ]
        path = self._notation_path(board, notation)

        exact = [move for move in candidates if move.path == path]
        if exact:
            candidates = exact
        else:
            candidates = [
                move
                for move in candidates
                if move.from_square == path[0] and move.to_square == path[-1]
            ]

        if len(candidates) != 1:
            separator = "x" if is_capture else "-"
            raise ValueError(
                f"Ход {separator.join(map(str, notation))} игрока "
                f"{player.name} не определён однозначно "
                f"(совпадений: {len(candidates)})"
            )
        return candidates[0]
