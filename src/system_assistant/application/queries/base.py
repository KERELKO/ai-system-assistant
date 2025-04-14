from abc import ABC, abstractmethod
from typing import Any


class Query:
    ...


class BaseQueryHandler[T: Query, R: Any](ABC):
    @abstractmethod
    async def handle(self, query: T) -> R:
        ...
