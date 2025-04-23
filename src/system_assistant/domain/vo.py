from typing import Literal
from dataclasses import dataclass

type ID = str

type AssistantModel = str


Sender = Literal['user', 'assistant']


@dataclass(eq=False)
class Message:
    sender: Sender
    content: str
