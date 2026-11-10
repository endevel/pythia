from collections.abc import Callable, Mapping

from pythia.core import Player, Rank
from pythia.core.piece import Piece
from pythia.core.square_state import SquareState


def fen_from_states(
    states: Mapping[int, SquareState],
    number_of: Callable[[int], int],
    start_color: Player,
) -> str:
    """Собирает FEN (PDN) из отображения «внутренний индекс -> состояние клетки».

    Аргументы:
        states: состояния клеток по внутренним индексам плоского массива.
        number_of: функция перевода внутреннего индекса в номер игрового поля
            (1..N); вызывается только для клеток с фигурами.
        start_color: игрок, чей ход в позиции.

    Формат: <цвет хода>:W<номера белых>:B<номера чёрных>, дамки помечаются
    префиксом "K". Номера в каждой секции отсортированы по возрастанию.
    """
    white: list[tuple[int, str]] = []
    black: list[tuple[int, str]] = []
    for ndx, state in states.items():
        if state in (SquareState.EMPTY, SquareState.TAKEN, SquareState.OUT_OF_BOARD):
            continue
        number = number_of(ndx)
        token = f"K{number}" if "KING" in state.name else str(number)
        if "WHITE" in state.name:
            white.append((number, token))
        else:
            black.append((number, token))

    white_section = "W" + ",".join(t for _, t in sorted(white))
    black_section = "B" + ",".join(t for _, t in sorted(black))
    color = "W" if start_color == Player.WHITE else "B"
    return f"{color}:{white_section}:{black_section}"


class Fen:
    def __init__(self):
        self.__start_color = Player.WHITE
        self.__pieces: list[Piece] = list()

    def parse(self, position: str):
        pieces = self.__pieces
        pieces.clear()

        color_section, *piece_sections = position.split(":")
        self.__start_color = Player.WHITE if color_section[0].upper() == "W" else Player.BLACK

        for section in piece_sections:
            owner = Player.WHITE if section[0].upper() == "W" else Player.BLACK
            body = section[1:]
            if body.endswith("."):
                body = body[:-1]

            for token in body.split(","):
                # Пустая секция (сторона без фигур) даёт пустой токен.
                if not token:
                    continue
                if token[0] in "Kk":
                    pieces.append(Piece(owner, Rank.KING, int(token[1:])))
                else:
                    pieces.append(Piece(owner, Rank.MAN, int(token)))

    @property
    def start_color(self) -> Player:
        return self.__start_color

    @property
    def pieces(self) -> list[Piece]:
        return self.__pieces
