import base64

import httpx
from loguru import logger

from system_assistant.core import ROOT
from system_assistant.core.types import Output, Speech
from system_assistant.core.exceptions import UnexpectedApplicationError, ApplicationException

from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService


GOOGLE_TEXT_TO_SPEECH_BASE_URL = 'https://texttospeech.googleapis.com'


class GoogleTextToSpeechService(BaseTextToSpeechService):
    def __init__(self, api_key: str):
        self.__api_key = api_key

    async def synthesize(self, text: str, output: Output) -> Speech:
        async with httpx.AsyncClient(
            base_url=GOOGLE_TEXT_TO_SPEECH_BASE_URL, params={'key': self.__api_key},
        ) as client:
            request_body = {
                'input': {'text': text},
                'voice': {'languageCode': 'en-US', 'ssmlGender': 'MALE'},
                'audioConfig': {'audioEncoding': 'MP3'},
            }
            response = await client.post('/v1/text:synthesize', json=request_body)
            data = response.json()
            if not response.is_success:
                logger.error(msg := f'Failed to convert text to speech: {data}')
                raise UnexpectedApplicationError(msg)
            audio_content = base64.b64decode(data['audioContent'])

        if output == 'bytes':
            return audio_content
        elif output == 'file':
            file_name = f'audio({len(text)}).mp3'
            with open(path := (ROOT / 'audio' / file_name), '+wb') as file:
                file.write(audio_content)
                return path
        else:
            raise ApplicationException(f'"{output}" is not supported as output format')
