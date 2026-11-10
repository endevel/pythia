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
  корректируется на `ply`, чтобы поиск предпочитал быструю победу.
"""

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
            score = -self._negamax(
                depth - 1,
                self._opponent(player),
                alpha=-beta,
                beta=-alpha,
                ply=1,
            )
            self._generator.unmake_move(undo)
            if score > best_score:
                best_score, best_move = score, move
            alpha = max(alpha, score)
        return SearchResult(move=best_move, score=best_score, depth=depth)

    def _negamax(
        self,
        depth: int,
        player: Player,
        alpha: int,
        beta: int,
        ply: int,
    ) -> int:
        """Негмакс с альфа-бета: счёт для стороны `player` в узле."""
        moves = self._generate_sorted(player)
        if not moves:
            # Ходов нет — все фигуры побиты или заперты: проигрыш.
            return -(WIN_SCORE - ply)
        if depth <= 0 and (not self._capture_extension or not moves[0].is_capture):
            return self._evaluator.evaluate(self._generator.states, player)
        best = -INF_SCORE
        for move in moves:
            undo = self._generator.make_move(move, player)
            score = -self._negamax(
                depth - 1,
                self._opponent(player),
                alpha=-beta,
                beta=-alpha,
                ply=ply + 1,
            )
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
