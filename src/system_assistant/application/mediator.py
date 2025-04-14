import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any

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

    async def handle_command(self, command: Command) -> list[Any]:
        results = await asyncio.gather(
            *[h.handle(command) for h in self.command_handlers[command.__class__]]
        )
        return results
