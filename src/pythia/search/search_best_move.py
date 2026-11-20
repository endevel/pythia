from __future__ import annotations

from pythia.core.move import Move
from pythia.core.player import Player
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.evaluation import Evaluation
from pythia.movegen.base import GenerateMoveList
from pythia.search.move_func import do_move, undo_move


class SearchBestMove:
    """Поиск лучшего хода методом альфа-бета отсечения.

    Поиск реализован в виде negamax-версии альфа-бета: оценка позиции
    всегда приводится к точке зрения игрока, чей ход, поэтому один и тот
    же код обслуживает и белых, и чёрных. Оценка
    :class:`~pythia.evaluation.evaluation.Evaluation` возвращается в пользу
    белых, поэтому для чёрных она меняет знак.

    Attributes:
        _movegen: Генератор ходов, используемый как образец. Для каждой
            позиции создаётся новый экземпляр того же типа, поскольку
            генератор привязан к конкретной доске и игроку.
        _evaluation: Оценка позиции.
    """

    # Оценка мата. Достаточно велика, чтобы перекрыть любую материальную
    # оценку, но далека от переполнения при сложении.
    _MATE = 1_000_000

    def __init__(
        self,
        movegen: GenerateMoveList | type[GenerateMoveList],
        evaluation: Evaluation,
    ):
        """Создаёт объект поиска.

        Args:
            movegen: Экземпляр генератора ходов или его класс. Генератор
                должен принимать ``(board, player)`` в конструкторе, как
                :class:`~pythia.movegen.russian_move_gen.RussianMoveGen` и
                :class:`~pythia.movegen.international_move_gen.InternationalMoveGen`.
            evaluation: Оценка позиции в пользу белых.
        """

        self._movegen = movegen
        self._evaluation = evaluation

    def search_best_move(
        self, board: DamBoard, depth: int = 3
    ) -> Move | None:
        """Возвращает лучший ход для игрока, чья очередь хода.

        Args:
            board: Текущая позиция. После поиска доска остаётся в исходном
                состоянии: все применённые ходы отменяются.
            depth: Глубина поиска в полуходах. Значение ``1`` означает,
                что оцениваются только позиции после одного хода.

        Returns:
            Лучший ход или ``None``, если у игрока нет допустимых ходов
            (позиция проиграна).

        Raises:
            ValueError: Если ``depth`` меньше единицы.
        """

        if depth < 1:
            raise ValueError("Глубина поиска должна быть не меньше 1")

        player = board.player_to_move
        moves = self._generate_moves(board, player)
        if not moves:
            return None

        alpha = -self._MATE - 1
        beta = self._MATE + 1
        best_score = alpha
        best_move = moves[0]

        for move in moves:
            do_move(board, move)
            score = -self._negamax(
                board, depth - 1, -beta, -alpha, ply=1
            )
            undo_move(board, move)

            if score > best_score:
                best_score = score
                best_move = move
            alpha = max(alpha, best_score)

        return best_move

    def _negamax(
        self,
        board: DamBoard,
        depth: int,
        alpha: int,
        beta: int,
        ply: int,
    ) -> int:
        """Оценивает позицию с точки зрения игрока, чей ход.

        Args:
            board: Текущая позиция.
            depth: Оставшаяся глубина поиска в полуходах.
            alpha: Нижняя граница окна поиска.
            beta: Верхняя граница окна поиска.
            ply: Число полуходов от корня. Используется для того, чтобы
                предпочитать более быстрый мат и более позднее поражение.

        Returns:
            Оценка позиции в пользу игрока, чей ход.
        """

        player = board.player_to_move
        moves = self._generate_moves(board, player)

        if not moves:
            # Игроку нечем ходить — он проиграл. Чем больше полуходов
            # прошло, тем позже наступило поражение, поэтому добавляем ply.
            return -self._MATE + ply

        if depth <= 0:
            return self._evaluate(board, player)

        best_score = -self._MATE - 1
        for move in moves:
            do_move(board, move)
            score = -self._negamax(
                board, depth - 1, -beta, -alpha, ply + 1
            )
            undo_move(board, move)

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                # Остальные ходы не могут улучшить результат для
                # максимизирующего игрока — окно отсекается.
                break

        return best_score

    def _generate_moves(
        self, board: DamBoard, player: Player
    ) -> list[Move]:
        """Создаёт генератор для позиции и возвращает список ходов."""

        movegen = self._movegen
        if isinstance(movegen, type):
            generator = movegen(board, player)
        else:
            generator = type(movegen)(board, player)
        return generator.generate_move_list()

    def _evaluate(self, board: DamBoard, player: Player) -> int:
        """Возвращает оценку позиции с точки зрения игрока ``player``."""

        score = self._evaluation.evaluate(board)
        return score if player == Player.WHITE else -score
