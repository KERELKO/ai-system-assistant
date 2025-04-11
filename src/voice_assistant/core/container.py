from functools import cache

from punq import Container, Scope  # type: ignore[import-untyped]

from voice_assistant.application.commands.generate_ai_voice_response import (
    GenerateAIVoiceResponseCommand, GenerateAIVoiceResponseCommandHandler)
from voice_assistant.application.mediator import Mediator
from voice_assistant.application.services.ai.base import AIAgent
from voice_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from voice_assistant.core.config import Config
from voice_assistant.infrastructure.services.ai.deepseek import DeepSeek
from voice_assistant.infrastructure.services.text_to_speech.google import \
    GoogleTextToSpeechService
from voice_assistant.infrastructure.services.sound.base import SoundService
from voice_assistant.infrastructure.services.sound.mpg123 import MPG123SoundService
from voice_assistant.infrastructure.services.ai.fake import FakeAIAgent


@cache
def init_container() -> Container:
    """Function to initialize DI container"""

    container = Container()

    config = Config()
    container.register(Config, instance=config)

    # ai_agent = FakeAIAgent()
    ai_agent = DeepSeek(config.deepseek_api_token)
    container.register(AIAgent, instance=ai_agent)

    text_to_speech_service = GoogleTextToSpeechService(config.google_api_token)
    container.register(
        BaseTextToSpeechService, instance=text_to_speech_service,
    )

    container.register(SoundService, MPG123SoundService, scope=Scope.transient)

    mediator = Mediator(
        command_handlers={
            GenerateAIVoiceResponseCommand: [
                GenerateAIVoiceResponseCommandHandler(text_to_speech_service, ai_agent)
            ]
        }
    )
    container.register(Mediator, instance=mediator, scope=Scope.singleton)

    return container
