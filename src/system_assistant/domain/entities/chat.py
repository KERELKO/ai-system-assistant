# mypy: disable-error-code = "misc"
from dataclasses import dataclass, field

from system_assistant.domain.vo import ID, Message


@dataclass(slots=True)
class Chat:
    id: ID
    title: str
    messages: list[Message] = field(default_factory=list)

    def add_message(self, message: Message):
        self.messages.append(message)
