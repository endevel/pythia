from pythia.core import Piece, Player


class Fen:
    def __init__(self):
        self.__start_color = Player.WHITE
        self.__pieces: set[Piece]

    def _parse_pieces(self, fen: str):
        piece = Piece(Player.WHITE, 0)
        # if fen[0].upper() == "W":
        #    piece = Piece(Player.WHITE, 0)
        if fen[0].upper() == "B":
            piece.change_owner()
        fen = fen.replace(fen[0], "")
        last_char = fen[-1]
        if last_char == ".":
            fen = fen[:-1]

        pieces: list[str] = fen.split(",")
        for piece_str in pieces:
            if piece_str[0].upper() == "K":
                piece.promote()
                piece_str = piece_str.replace(piece_str[0], "")
            square_ndx = int(piece_str)
            piece.set_square_ndx(square_ndx)
            self.__pieces.add(piece)

    def parse(self, position: str):
        self.__pieces.clear()
        items: list[str] = position.split(":")
        self._start_color = Player.WHITE if items[0].upper() == "W" else Player.BLACK
        for item in items[1:]:
            self._parse_pieces(item)

    @property
    def start_color(self) -> Player:
        return self.__start_color

    @property
    def pieces(self) -> set[Piece]:
        return self.__pieces
