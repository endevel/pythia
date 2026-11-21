from pythia.core.board_size import BoardSize
from pythia.core.game_type import GameType
from pythia.core.move import move_to_str
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.evaluation import Evaluation
from pythia.evaluation.international_evaluation import InternationalEvaluation
from pythia.evaluation.russian_evaluation import RussianEvaluation
from pythia.movegen.base import GenerateMoveList
from pythia.movegen.international_move_gen import InternationalMoveGen
from pythia.movegen.russian_move_gen import RussianMoveGen
from pythia.search.move_func import do_move as apply_move
from pythia.search.search_best_move import SearchBestMove

INTERNATIONAL_START_FEN = (
    "W:W31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50:"
    "B1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20"
)

RUSSIAN_START_FEN = "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"
BRAZILIAN_START_FEN = (
    "W:W21,22,23,24,25,26,27,28,29,30,31,32:B1,2,3,4,5,6,7,8,9,10,11,12"
)

# Таблицы соответствия типа игры её параметрам. Использование словарей
# вместо цепочек if/elif гарантирует, что для каждого элемента GameType
# задано значение, и избавляет от неявного возврата None.
_BOARD_SIZES: dict[GameType, BoardSize] = {
    GameType.INTERNATIONAL: BoardSize.BIG,
    GameType.RUSSIAN: BoardSize.STANDARD,
    GameType.BRAZILIAN: BoardSize.STANDARD,
}

_START_FENS: dict[GameType, str] = {
    GameType.INTERNATIONAL: INTERNATIONAL_START_FEN,
    GameType.RUSSIAN: RUSSIAN_START_FEN,
    GameType.BRAZILIAN: BRAZILIAN_START_FEN,
}

# Хранятся именно классы, а не экземпляры: конструктор генератора требует
# доску и игрока, поэтому экземпляр создаётся для каждой конкретной позиции
# внутри SearchBestMove.
_MOVE_GENERATORS: dict[GameType, type[GenerateMoveList]] = {
    GameType.INTERNATIONAL: InternationalMoveGen,
    GameType.RUSSIAN: RussianMoveGen,
    GameType.BRAZILIAN: InternationalMoveGen,
}

_EVALUATIONS: dict[GameType, type[Evaluation]] = {
    GameType.INTERNATIONAL: InternationalEvaluation,
    GameType.RUSSIAN: RussianEvaluation,
    GameType.BRAZILIAN: InternationalEvaluation,
}


class Engine:
    def __init__(self, game_type: GameType = GameType.INTERNATIONAL):
        if game_type not in _BOARD_SIZES:
            raise ValueError(f"Неподдерживаемый тип игры: {game_type!r}")

        self._game_type = game_type
        self._board: DamBoard = self._create_board()
        self._move_generator: type[GenerateMoveList] = self._create_move_generator()
        self._evaluator: Evaluation = self._create_evaluator()
        self._init_board()
        self._move_searcher: SearchBestMove = self._create_move_searcher()

    def _create_board(self) -> DamBoard:
        return DamBoard(_BOARD_SIZES[self._game_type])

    def _init_board(self) -> None:
        self._board.setup(_START_FENS[self._game_type])

    def _create_evaluator(self) -> Evaluation:
        return _EVALUATIONS[self._game_type]()

    def _create_move_generator(self) -> type[GenerateMoveList]:
        return _MOVE_GENERATORS[self._game_type]

    def _create_move_searcher(self) -> SearchBestMove:
        return SearchBestMove(self._move_generator, self._evaluator)

    def calculate_best_move(self) -> None:
        best_move = self._move_searcher.calculate(self._board)
        if best_move is None:
            print("Допустимых ходов нет")
            return
        print(move_to_str(best_move, self._board))

    def run(self) -> None:
        ending: bool = False
        while not ending:
            try:
                command_line = input(">>> ").strip()
            except (EOFError, KeyboardInterrupt):
                # Завершаем работу по Ctrl+C или концу ввода, не выбрасывая
                # трассировку стека наружу.
                print()
                print("Выход...")
                break

            # Если пользователь просто нажал Enter, начинаем новую итерацию цикла
            if not command_line:
                continue

            # Разбиваем строку на части. Первый элемент — команда, остальные — аргументы
            parts = command_line.split()
            command = parts[0].lower()
            args = parts[1:]

            if command == "exit":
                print("Выход...")
                ending = True
            elif command == "help":
                print("Доступные команды:")
                print("  help                 - показать это сообщение")
                print("  exit                 - выйти из программы")
                print("  greet [имя]          - поздороваться")
                print("  do_move <откуда> <куда> - сделать ход на доске")
            elif command == "greet":
                if args:
                    print(f"Привет, {args[0]}!")
                else:
                    print("Привет, мир!")
            elif command == "do_move":
                print("Выполняем ход...")
                self.calculate_best_move()
            else:
                print(f"Неизвестная команда: {command}. Введите 'help'.")

    def _handle_do_move(self, args: list[str]) -> None:
        """Выполняет ход, заданный номерами полей: ``do_move <откуда> <куда>``.

        Ход ищется среди легальных ходов текущего игрока, поэтому
        недопустимые ходы (в том числе нарушающие правило обязательного
        взятия) не применяются.
        """

        if len(args) != 2:
            print("Использование: do_move <откуда> <куда> (номера полей)")
            return

        try:
            from_number, to_number = (int(value) for value in args)
        except ValueError:
            print("Номера полей должны быть целыми числами")
            return

        player = self._board.player_to_move
        moves = self._move_generator(self._board, player).generate_move_list()
        for move in moves:
            if (
                self._board.number_at(move.from_square) == from_number
                and self._board.number_at(move.to_square) == to_number
            ):
                apply_move(self._board, move)
                fen = self._board.to_fen(self._board.player_to_move)
                print(f"Ход выполнен. Позиция: {fen}")
                return

        print("Недопустимый ход")

    @property
    def board(self) -> DamBoard:
        return self._board
