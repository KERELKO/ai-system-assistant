import asyncio

from .application.commands.generate_ai_voice_response import (
    GenerateAIVoiceResponseCommand, GenerateAIVoiceResponseCommandHandler)
from .application.mediator import Mediator
from .core import ROOT
from .core.config import Config
from .infrastructure.services.ai.deepseek import DeepSeek
from .infrastructure.services.text_to_speech.google import \
    GoogleTextToSpeechService


async def main(text: str):
    config = Config()

    ai_agent = DeepSeek(config.deepseek_api_token)
    text_to_speech_service = GoogleTextToSpeechService(config.google_api_token)

    mediator = Mediator(
        command_handlers={
            GenerateAIVoiceResponseCommand: [
                GenerateAIVoiceResponseCommandHandler(text_to_speech_service, ai_agent)
            ]
        }
    )

    response: bytes = (
        await mediator.handle_command(GenerateAIVoiceResponseCommand(text, 'bytes'))
    )[0]

    with open(ROOT / 'speech.mp3', '+bw') as file:
        file.write(response)


if __name__ == "__main__":
    asyncio.run(main('I got it!!!'))
