from enum import StrEnum, auto
import uuid


type ID = str

type AssistantModel = str


def generate_id() -> ID:
    return str(uuid.uuid4())


class Sender(StrEnum):
    USER = auto()
    ASSISTANT = auto()
