from __future__ import annotations

import math
import time

from pythia.core.move import Move
from pythia.core.player import Player
from pythia.damboard.damboard import DamBoard
from pythia.evaluation.evaluation import Evaluation
from pythia.movegen.base import GenerateMoveList
from pythia.search.move_func import do_move, undo_move


class SearchTimeout(Exception):
    """Поиск прерван, потому что истекло отведённое время."""


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

    # Доля лимита времени, после которой поиск прерывается. Оставшиеся
    # 25% — запас на возврат результата и накладные расходы.
    _TIME_LIMIT_RATIO = 0.75

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
        self,
        board: DamBoard,
        depth: int = 3,
        deadline: float | None = None,
    ) -> Move | None:
        """Возвращает лучший ход для игрока, чья очередь хода.

        Args:
            board: Текущая позиция. После поиска доска остаётся в исходном
                состоянии: все применённые ходы отменяются, в том числе
                при прерывании поиска.
            depth: Глубина поиска в полуходах. Значение ``1`` означает,
                что оцениваются только позиции после одного хода.
            deadline: Абсолютное время (значение ``time.monotonic()``),
                после которого поиск должен быть прерван. ``None`` —
                поиск без ограничения по времени.

        Returns:
            Лучший ход или ``None``, если у игрока нет допустимых ходов
            (позиция проиграна).

        Raises:
            ValueError: Если ``depth`` меньше единицы.
            SearchTimeout: Если текущее время достигло ``deadline``.
        """

        if depth < 1:
            raise ValueError("Глубина поиска должна быть не меньше 1")

        self._check_deadline(deadline)

        player = board.player_to_move
        moves = self._generate_moves(board, player)
        if not moves:
            return None

        alpha = -self._MATE - 1
        beta = self._MATE + 1
        best_score = alpha
        best_move = moves[0]

        for move in moves:
            self._check_deadline(deadline)
            do_move(board, move)
            try:
                score = -self._negamax(
                    board,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply=1,
                    deadline=deadline,
                )
            finally:
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
        deadline: float | None = None,
    ) -> int:
        """Оценивает позицию с точки зрения игрока, чей ход.

        Если в позиции есть ударные ходы, они рассматриваются всегда —
        в том числе при исчерпанной глубине (``depth <= 0``). Статическая
        оценка возвращается только для позиции без обязательных взятий.

        Args:
            board: Текущая позиция.
            depth: Оставшаяся глубина поиска в полуходах.
            alpha: Нижняя граница окна поиска.
            beta: Верхняя граница окна поиска.
            ply: Число полуходов от корня. Используется для того, чтобы
                предпочитать более быстрый мат и более позднее поражение.
            deadline: Абсолютное время, после которого поиск должен быть
                прерван, или ``None``.

        Returns:
            Оценка позиции в пользу игрока, чей ход.

        Raises:
            SearchTimeout: Если текущее время достигло ``deadline``.
        """

        self._check_deadline(deadline)

        player = board.player_to_move
        moves = self._generate_moves(board, player)

        if not moves:
            # Игроку нечем ходить — он проиграл. Чем больше полуходов
            # прошло, тем позже наступило поражение, поэтому добавляем ply.
            return -self._MATE + ply

        # В шашках взятие обязательно, поэтому позицию с ударными ходами
        # нельзя оценивать статически: сначала нужно рассмотреть сами
        # взятия, даже если лимит глубины уже исчерпан. Так поиск
        # продолжается по цепочке обязательных взятий и лишь затем
        # переходит к оценке позиции.
        captures = [move for move in moves if move.taken]
        if captures:
            moves = captures
        elif depth <= 0:
            return self._evaluate(board, player)

        best_score = -self._MATE - 1
        for move in moves:
            do_move(board, move)
            try:
                score = -self._negamax(
                    board,
                    depth - 1,
                    -beta,
                    -alpha,
                    ply + 1,
                    deadline,
                )
            finally:
                undo_move(board, move)

            best_score = max(best_score, score)
            alpha = max(alpha, best_score)
            if alpha >= beta:
                # Остальные ходы не могут улучшить результат для
                # максимизирующего игрока — окно отсекается.
                break

        return best_score

    @staticmethod
    def _check_deadline(deadline: float | None) -> None:
        """Прерывает поиск, если достигнут дедлайн."""

        if deadline is not None and time.monotonic() >= deadline:
            raise SearchTimeout

    def calculate(
        self,
        board: DamBoard,
        time_limit: float = 1.0,
    ) -> Move | None:
        """Ищет лучший ход с ограничением времени.

        Выполняет итеративное углубление: последовательно вызывает
        :meth:`search_best_move` с глубиной ``1, 2, 3, ...``, пока не
        истечёт 75% отведённого времени. Результат последней полностью
        завершённой итерации считается лучшим ходом.

        Args:
            board: Текущая позиция. После поиска доска остаётся в исходном
                состоянии.
            time_limit: Лимит времени на обдумывание хода в секундах.
                По умолчанию — 1 секунда.

        Returns:
            Лучший найденный ход или ``None``, если у игрока нет
            допустимых ходов.

        Raises:
            ValueError: Если ``time_limit`` не является положительным
                конечным числом.
        """

        if not math.isfinite(time_limit) or time_limit <= 0:
            raise ValueError("Лимит времени должен быть положительным конечным числом")

        start = time.monotonic()
        deadline = start + time_limit * self._TIME_LIMIT_RATIO

        best_move: Move | None = None
        depth = 1
        while True:
            try:
                move = self.search_best_move(board, depth, deadline=deadline)
            except SearchTimeout:
                break

            if move is None:
                return None

            best_move = move
            depth += 1

        if best_move is not None:
            return best_move

        # Даже первая итерация не успела завершиться. Возвращаем первый
        # допустимый ход, чтобы не оставить игрока без хода.
        moves = self._generate_moves(board, board.player_to_move)
        return moves[0] if moves else None

    def _generate_moves(self, board: DamBoard, player: Player) -> list[Move]:
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
