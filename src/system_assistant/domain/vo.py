from typing import Literal
from dataclasses import dataclass

type ID = str

type AssistantModel = str


Sender = Literal['user', 'assistant']


@dataclass(slots=True)
class Message:
    sender: Sender
    content: str
