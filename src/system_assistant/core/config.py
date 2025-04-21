import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


class ConfigError(Exception):
    ...


@dataclass(eq=False, slots=True)
class Config:
    _deepseek_api_key: str = ''
    _google_api_key: str = ''
    _gemini_api_key: str = ''
    dgraph_url: str = os.getenv('DGRAPH_URL', 'http://localhost:8080/graphql')

    @property
    def google_api_key(self) -> str:
        if (key := self._google_api_key):
            return key
        key = os.getenv('GOOGLE_API_KEY', '')
        if not key:
            raise ConfigError('No value for "google_api_key"')
        self._google_api_key = key
        return key

    @property
    def deepseek_api_key(self) -> str:
        if (key := self._deepseek_api_key):
            return key
        key = os.getenv('DEEPSEEK_API_KEY', '')
        if not key:
            raise ConfigError('No value for "deepseek_api_key"')
        self._deepseek_api_key = key
        return key

    @property
    def gemini_api_key(self) -> str:
        if (key := self._gemini_api_key):
            return key
        key = os.getenv('GEMINI_API_KEY', '')
        if not key:
            raise ConfigError('No value for "gemini_api_key"')
        self._gemini_api_key = key
        return key

    def __post_init__(self):
        for field_name in self.__slots__:
            if getattr(self, field_name, None) is None:
                raise ConfigError(f'"{field_name}" has invalid value')
