"""Представление хода — см. п.3 movegen.md.

Ход — это последовательность шагов (нужно и для PDN, и для анимации).
`Move` намеренно хранит только номера полей (FMJD-нумерация, 1..N) —
этого достаточно для PDN, анимации и сортировки ходов.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Step:
    """Один шаг хода.

    Attributes:
        to: номер поля, на которое встаёт фигура после шага.
        captured: номер поля побитой фигуры (None для тихого шага).
    """

    to: int
    captured: int | None = None


@dataclass(frozen=True)
class Move:
    """Ход в терминах номеров игровых полей.

    Attributes:
        path: номера полей: исходное → ... → конечное.
        captured: номера побитых полей (пусто для тихого хода).
        promotes: True, если ходившая простая завершила ход на строке
            превращения (см. `Rules.promotion_rows`).
    """

    path: tuple[int, ...]
    captured: tuple[int, ...]
    promotes: bool = False

    @property
    def is_capture(self) -> bool:
        return bool(self.captured)
