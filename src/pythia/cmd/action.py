from typing_extensions import Protocol


class Action(Protocol):
    def execute(self, params) -> None:
        raise NotImplementedError