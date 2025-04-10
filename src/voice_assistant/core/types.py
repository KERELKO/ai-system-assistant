from pathlib import Path
from typing import Literal


class URL(str):
    def __init__(self, string: str):
        if not string.startswith('http://') or not string.startswith('https://'):
            raise ValueError('string does not start with http or https')
        self.string = string


type Speech = Path | URL | bytes
type Output = Literal['file', 'bytes', 's3']
