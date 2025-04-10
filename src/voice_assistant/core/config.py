from dataclasses import dataclass
import os
from dotenv import load_dotenv


load_dotenv()


@dataclass(eq=False, frozen=True, slots=True)
class Config:
    deepseek_api_token: str = os.getenv('DEEPSEEK_API_TOKEN', '')
    google_api_token: str = os.getenv('GOOGLE_API_TOKEN', '')

    def __post_init__(self):
        for field_name in self.__slots__:
            if not getattr(self, field_name):
                raise ValueError(f'Config error: "{field_name}" has invalid value')
