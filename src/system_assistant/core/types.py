from pathlib import Path
from typing import Literal


class URL(str):
    """A custom string subclass that enforces HTTP/HTTPS URLs."""
    def __new__(cls, url: str) -> 'URL':
        if not (url.startswith('http://') or url.startswith('https://')):
            raise ValueError("URL must start with 'http://' or 'https://'")
        return super().__new__(cls, url)


type Speech = Path | URL | bytes
type Output = Literal['file', 'bytes', 's3']
