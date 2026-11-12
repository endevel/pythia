"""Поиск лучшего хода — негмакс с альфа-бета отсечениями (пп. 3–5 search.md).

Ключевые решения:

- `Search` владеет одним `MoveGenerator`: позиция в узлах дерева
  применяется/откатывается через `make_move`/`unmake_move`, без
  пересоздания генератора на каждый узел;
- счёт везде с точки зрения стороны, чей ход (негмакс): ход противника
  возвращает счёт, знак которого инвертируется;
- форсированные взятия продлеваются за границу глубины (упрощённый
  quiescence): цепочка взятий всегда доигрывается до конца, иначе оценка
  на границе глубины «подвешивала» бы шашки под боем;
- ходы сортируются для усиления отсечений: сначала более длинные взятия,
  затем превращения;
- ходов нет — игрок проиграл (все фигуры побиты или заперты), счёт
  корректируется на `ply`, чтобы поиск предпочитал быструю победу;
- `best_move_timed` ищет с нарастающей глубиной в пределах бюджета
  времени (по умолчанию 1 с): новый перебор не запускается после 70%
  бюджета, а начатый прерывается исключением при его исчерпании.
"""

import time
from dataclasses import dataclass

from pythia.core.player import Player
from pythia.damboard.damboard import Damboard
from pythia.movegen.generator import MoveGenerator
from pythia.movegen.move import Move
from pythia.movegen.rules import RUSSIAN, Rules
from pythia.search.evaluation import Evaluator, MaterialEvaluator

# Базовая оценка победы/проигрыша; в счёт подмешивается `ply`, поэтому
# «мат в 1» (~WIN_SCORE - 1) всегда предпочтительнее «мата в 5».
WIN_SCORE = 1_000_000
INF_SCORE = 10 * WIN_SCORE

# Доля бюджета времени, после превышения которой не запускается следующий
# (более глубокий) перебор: каждый следующий уровень дерева занимает больше
# времени, чем предыдущий, поэтому перебор, начатый при исчерпании 70%
# бюджета, почти наверняка не уложится в оставшиеся 30%.
_SOFT_TIME_RATIO = 0.7


class _SearchTimeout(Exception):
    """Внутреннее исключение: бюджет времени поиска исчерпан."""


@dataclass(frozen=True)
class SearchResult:
    """Результат поиска.

    Attributes:
        move: лучший ход; None, если ходов нет (позиция проиграна).
        score: оценка позиции для стороны, переданной в `best_move`.
        depth: глубина перебора в полуходах.
    """

    move: Move | None
    score: int
    depth: int


class Search:
    """Поиск лучшего хода: негмакс + альфа-бета отсечения.

    Attributes:
        board: доска с исходной позицией (не мутируется).
        rules: параметры варианта игры (см. `pythia.movegen.rules`).
        evaluator: стратегия оценки позиции; по умолчанию — материал.
        capture_extension: доигрывать форсированные взятия за границей
            глубины (упрощённый quiescence).
    """

    def __init__(
        self,
        board: Damboard,
        rules: Rules = RUSSIAN,
        evaluator: Evaluator | None = None,
        capture_extension: bool = True,
    ):
        self._generator = MoveGenerator(board, rules)
        self._evaluator: Evaluator = evaluator if evaluator is not None else MaterialEvaluator()
        self._capture_extension = capture_extension
        self._deadline: float | None = None

    def best_move(self, player: Player, depth: int = 6) -> SearchResult:
        """Лучший ход для `player` перебором на `depth` полуходов.

        Возвращает ход и оценку позиции для `player`; если ходов нет
        (проигрыш), `move` равен None, а счёт — проигрышный.
        """
        moves = self._generate_sorted(player)
        if not moves:
            return SearchResult(move=None, score=-WIN_SCORE, depth=depth)
        best_move: Move | None = None
        best_score = -INF_SCORE
        alpha, beta = -INF_SCORE, INF_SCORE
        for move in moves:
            undo = self._generator.make_move(move, player)
            try:
                score = -self._negamax(
                    depth - 1,
                    self._opponent(player),
                    alpha=-beta,
                    beta=-alpha,
                    ply=1,
                )
            finally:
                # finally (а не только в штатном сценарии) — чтобы при
                # прерывании по времени ходы откатывались на каждом кадре.
                self._generator.unmake_move(undo)
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, score)
        return SearchResult(move=best_move, score=best_score, depth=depth)

    def best_move_timed(self, player: Player, time_limit: float = 1.0) -> SearchResult:
        """Лучший ход для `player` за отведённое `time_limit` секунд.

        Последовательно перебирает нарастающие глубины (2, 3, ...), пока
        позволяет бюджет времени. Новый перебор не запускается, если
        потрачено более 70% бюджета (см. `_SOFT_TIME_RATIO`); начатый
        перебор прерывается при полном исчерпании бюджета. Возвращается
        результат последней завершённой глубины (минимум — глубина 1,
        выполняется мгновенно как страховка).
        """
        start = time.perf_counter()
        self._deadline = start + time_limit
        result = self.best_move(player, depth=1)
        try:
            depth = 2
            while time.perf_counter() - start <= _SOFT_TIME_RATIO * time_limit:
                result = self.best_move(player, depth=depth)
                depth += 1
        except _SearchTimeout:
            pass  # бюджет исчерпан — используем последнюю завершённую глубину
        finally:
            self._deadline = None
        return result

    def _negamax(
        self,
        depth: int,
        player: Player,
        alpha: int,
        beta: int,
        ply: int,
    ) -> int:
        """Негмакс с альфа-бета: счёт для стороны `player` в узле."""
        if self._deadline is not None and time.perf_counter() >= self._deadline:
            # Проверка до generate/make_move — откатывать здесь нечего.
            raise _SearchTimeout
        moves = self._generate_sorted(player)
        if not moves:
            # Ходов нет — все фигуры побиты или заперты: проигрыш.
            return -(WIN_SCORE - ply)
        if depth <= 0 and (not self._capture_extension or not moves[0].is_capture):
            return self._evaluator.evaluate(self._generator.states, player)
        best = -INF_SCORE
        for move in moves:
            undo = self._generator.make_move(move, player)
            try:
                score = -self._negamax(
                    depth - 1,
                    self._opponent(player),
                    alpha=-beta,
                    beta=-alpha,
                    ply=ply + 1,
                )
            finally:
                self._generator.unmake_move(undo)
            if score > best:
                best = score
            if best > alpha:
                alpha = best
            if alpha >= beta:
                break  # отсечение: у противника есть ход не хуже
        return best

    def _generate_sorted(self, player: Player) -> list[Move]:
        """Ходы игрока, отсортированные для усиления отсечений.

        Сначала взятия (генератор и так возвращает их первыми), среди
        них — с большим числом побитых фигур; затем превращения.
        """
        moves = self._generator.generate(player)
        moves.sort(key=lambda move: (len(move.captured), move.promotes), reverse=True)
        return moves

    @staticmethod
    def _opponent(player: Player) -> Player:
        return Player.BLACK if player == Player.WHITE else Player.WHITE
