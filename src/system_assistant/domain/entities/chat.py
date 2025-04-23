# mypy: disable-error-code = "misc"
from dataclasses import dataclass, field

from system_assistant.domain.vo import ID, Message


@dataclass(eq=False)
class Chat:
    id: ID
    title: str
    messages: list[Message] = field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)

    def __eq__(self, other) -> bool:
        return self.id == other.id if isinstance(other, Chat) else False

    def __hash__(self) -> int:
        return hash(self.id)
