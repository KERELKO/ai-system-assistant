from functools import cache

from punq import Container, Scope  # type: ignore[import-untyped]
from langgraph.checkpoint.memory import MemorySaver

from system_assistant.application.commands.generate_ai_voice_response import (
    GenerateAIVoiceResponseCommand, GenerateAIVoiceResponseCommandHandler)
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import LLM, FakeLLM  # noqa
from system_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from system_assistant.core.config import Config
from system_assistant.infrastructure.services.ai.deepseek import DeepSeek  # noqa
from system_assistant.infrastructure.services.ai.gemini import Gemini  # noqa
from system_assistant.infrastructure.services.text_to_speech.google import \
    GoogleTextToSpeechService
from system_assistant.infrastructure.services.sound.base import SoundService
from system_assistant.infrastructure.services.sound.mpg123 import MPG123SoundService
from system_assistant.infrastructure.services.ai.openai_agent import OpenAIAgent
from system_assistant.infrastructure.services.ai.tools import TOOLS


@cache
def init_container() -> Container:
    """Function to initialize DI container"""

    container = Container()

    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    # llm = FakeLLM()
    llm = Gemini(config.gemini_api_key)
    # llm = DeepSeek(config.deepseek_api_key)
    container.register(LLM, instance=llm)

    text_to_speech_service = GoogleTextToSpeechService(config.google_api_key)
    container.register(
        BaseTextToSpeechService, instance=text_to_speech_service,
    )

    container.register(SoundService, MPG123SoundService, scope=Scope.transient)
    container.register(
        OpenAIAgent,
        instance=OpenAIAgent(config, memory_saver=MemorySaver(), tools=TOOLS, llm='gemini'),
    )

    mediator = Mediator(
        command_handlers={
            GenerateAIVoiceResponseCommand: [
                GenerateAIVoiceResponseCommandHandler(text_to_speech_service, llm)
            ]
        }
    )
    container.register(Mediator, instance=mediator, scope=Scope.singleton)

    return container
