from typing import Literal, Required, TypedDict
import uuid
from dataclasses import dataclass

type ID = str

type AssistantModel = str


def generate_id() -> ID:
    return str(uuid.uuid4())


Sender = Literal['user', 'assistant']


@dataclass(slots=True)
class Message:
    sender: Sender
    content: str


class AIAnswer(TypedDict, total=True):
    chat_id: Required[ID]
    is_successful: Required[bool]
    content: str
