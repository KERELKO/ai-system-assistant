from abc import ABC, abstractmethod
from typing import Any


class Command:
    ...


class BaseCommandHandler[T: Command, R: Any](ABC):
    @abstractmethod
    async def handle(self, command: T) -> R:
        ...
