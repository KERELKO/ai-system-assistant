from dataclasses import dataclass

from system_assistant.domain.vo import ID

from .base import BaseCommandHandler, Command


@dataclass(eq=False, slots=True, repr=False)
class RequestSystemHelpCommand(Command):
    message: str
    chat_id: str


@dataclass(eq=False, repr=False, slots=True)
class Response:
    is_successful: bool
    chat_id: ID


class RequestSystemHelpCommandHandler(BaseCommandHandler[RequestSystemHelpCommand, Response]):
    async def handle(self, command: RequestSystemHelpCommand) -> Response:
        raise NotImplementedError
