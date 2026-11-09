from pythia.core import Player, Rank
from pythia.core.piece import Piece


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
