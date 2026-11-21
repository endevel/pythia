from collections.abc import Callable

from typing_extensions import Protocol


class Action(Protocol):
    def execute(self, callback: Callable[[], None]) -> None:
        raise NotImplementedError
