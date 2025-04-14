import subprocess


class MPG123SoundService:
    """
    Sound service that uses linux `mpg123` utility to play sound
    * Works only if you have `mpg123` installed on your machine
    """

    def play_sound(self, stream: bytes):
        subprocess.run(['mpg123', '-q', '-'], input=stream)
