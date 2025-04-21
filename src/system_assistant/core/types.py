import platform
import os

from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Required, TypedDict

from system_assistant.core import ROOT
from system_assistant.domain.vo import ID


class URL(str):
    """A custom string subclass that enforces HTTP/HTTPS URLs."""
    def __new__(cls, url: str) -> 'URL':
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with 'http://' or 'https://'")
        return super().__new__(cls, url)


type Speech = Path | URL | bytes
type Output = Literal['file', 'bytes']


@dataclass(eq=False, slots=True)
class SystemContext:
    operating_system: str
    distribution: str
    cwd: Path
    directory_list: list[str]

    @classmethod
    def default(cls, cwd: Path | None = None) -> 'SystemContext':
        return cls(
            operating_system=platform.system(),
            distribution=platform.freedesktop_os_release()['NAME'],
            cwd=cwd or ROOT,
            directory_list=os.listdir(),
        )


class AIAnswer(TypedDict, total=True):
    chat_id: Required[ID]
    is_successful: Required[bool]
    content: str
