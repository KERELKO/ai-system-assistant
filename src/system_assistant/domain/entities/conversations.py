# mypy: disable-error-code = "misc"
from dataclasses import dataclass, field

from system_assistant.domain.vo import ID, Sender


@dataclass(slots=True)
class Message:
    sender: Sender
    content: str


@dataclass(slots=True)
class Chat:
    id: ID
    title: str
    messages: list[Message] = field(default_factory=list)
