# mypy: disable-error-code = "misc"
from dataclasses import dataclass, field

from voice_assistant.domain.vo import ID, Sender, generate_id


@dataclass(slots=True)
class Message:
    id: ID = field(default_factory=generate_id, kw_only=True)
    sender: Sender
    body: str


@dataclass(slots=True)
class Chat:
    id: ID = field(default_factory=generate_id, kw_only=True)
    title: str
    messages: list[Message] = field(default_factory=list)
