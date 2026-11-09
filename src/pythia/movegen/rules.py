"""Правила игры как данные (Strategy) — см. пп. 2–3 movegen.md.

Различия русских и международных шашек не алгоритмические, а параметрические:
генератор один, а вся вариативность — в объекте `Rules`.
"""

from dataclasses import dataclass
from enum import Enum, auto


class CapturePriority(Enum):
    """Стратегия выбора цепочки взятия."""

    FREE_CHOICE = auto()  # русские: любая полная цепочка взятия допустима
    MAX_MAJORITY = auto()  # международные: обязательное «правило большинства»


class MidCapturePromotion(Enum):
    """Поведение простой шашки, достигшей дамочного поля в ходе взятия."""

    CONTINUE_AS_MAN = auto()  # международные: если простая в ходе взятия достигла
    # дамочного поля и далее может бить как простая шашка,
    # она обязана это сделать и при этом остаётся простой
    # до конца хода
    PROMOTES_AT_ONCE = auto()  # русские: простая превращается в дамку сразу, как
    # только достигла дамочного поля, и продолжает бой
    # уже как дамка


@dataclass(frozen=True)
class Rules:
    """Параметры варианта игры.

    Attributes:
        mid_capture_promotion: поведение простой шашки, достигшей дамочного
            поля в ходе взятия.
        capture_priority: стратегия выбора цепочки взятия.
        promotion_rows: строки превращения, отсчитываемые от геометрии доски;
            0 — самый дальний от игрока ряд (дамочный), 1 — предыдущий и т.д.
    """

    mid_capture_promotion: MidCapturePromotion
    capture_priority: CapturePriority
    promotion_rows: frozenset[int]


RUSSIAN = Rules(
    mid_capture_promotion=MidCapturePromotion.PROMOTES_AT_ONCE,
    capture_priority=CapturePriority.FREE_CHOICE,
    promotion_rows=frozenset({0}),
)

INTERNATIONAL = Rules(
    mid_capture_promotion=MidCapturePromotion.CONTINUE_AS_MAN,
    capture_priority=CapturePriority.MAX_MAJORITY,
    promotion_rows=frozenset({0}),
)
