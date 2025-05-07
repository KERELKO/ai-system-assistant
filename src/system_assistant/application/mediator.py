from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, overload

from system_assistant.application.commands.base import (BaseCommandHandler,
                                                        Command)
from system_assistant.application.queries.base import BaseQueryHandler, Query


@dataclass(eq=False, repr=False, slots=True)
class Mediator:
    query_handlers: dict[type[Query], BaseQueryHandler] = field(
        kw_only=True, default_factory=dict,
    )
    command_handlers: dict[type[Command], list[BaseCommandHandler]] = field(
        kw_only=True, default_factory=lambda: defaultdict(list)
    )

    async def handle_query(self, query: Query) -> Any:
        return await self.query_handlers[query.__class__].handle(query)

    async def handle_command(self, command: Command) -> Any:
        result = await self.command_handlers[command.__class__][0].handle(command)
        return result

    @overload
    def register_handlers(
        self, command_or_query: type[Query], handlers: list[BaseQueryHandler],
    ) -> None:
        ...

    @overload
    def register_handlers(
        self, command_or_query: type[Command], handlers: list[BaseCommandHandler],
    ) -> None:
        ...

    def register_handlers(self, command_or_query, handlers):
        if issubclass(command_or_query, Query):
            self.query_handlers[command_or_query] = handlers
        elif issubclass(command_or_query, Command):
            self.command_handlers[command_or_query] = handlers
