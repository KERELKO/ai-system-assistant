from typing import Protocol


class SoundService(Protocol):
    def play_sound(self, stream: bytes):
        ...
