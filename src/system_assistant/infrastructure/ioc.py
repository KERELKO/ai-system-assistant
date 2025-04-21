import typing as t
from functools import cache

from punq import Container, Scope  # type: ignore[import-untyped]

from system_assistant.application.commands.generate_ai_voice_response import (
    GenerateAIVoiceResponseCommandHandler
)
from system_assistant.application.commands.request_system_help import (
    RequestSystemHelpCommand, RequestSystemHelpCommandHandler)
from system_assistant.application.gateways.chat import ChatGateway, InMemoryChatGateway
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import (LLM,  # noqa
                                                           AIAgent, FakeAIAgent, FakeLLM)
from system_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from system_assistant.core.config import Config
from system_assistant.infrastructure.services.ai.deepseek import \
    DeepSeek, DeepSeekOpenAIAgent  # noqa
from system_assistant.infrastructure.services.ai.openai_agent import BaseReactOpenAIAgent
from system_assistant.infrastructure.services.ai.gemini import Gemini, GeminiOpenAIAgent  # noqa
from system_assistant.infrastructure.services.ai.tools import TOOLS
from system_assistant.infrastructure.services.sound.base import SoundService
from system_assistant.infrastructure.services.sound.mpg123 import \
    MPG123SoundService
from system_assistant.infrastructure.services.text_to_speech.google import \
    GoogleTextToSpeechService


@cache
def init_container(llm_type: t.Literal['deepseek', 'gemini', 'fake']) -> Container:
    """Function to initialize DI container"""

    container = Container()

    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    if llm_type == 'gemini':
        ai_agent: BaseReactOpenAIAgent = GeminiOpenAIAgent(config, tools=TOOLS)
        llm: LLM = Gemini(config.gemini_api_key)
        container.register(Gemini, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm, )
    elif llm_type == 'deepseek':
        ai_agent = DeepSeekOpenAIAgent(config, tools=TOOLS)
        llm = DeepSeek(config.deepseek_api_key)
        container.register(DeepSeek, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)
    elif llm_type == 'fake':
        llm = FakeLLM()
        container.register(LLM, FakeLLM)
        ai_agent = FakeAIAgent()  # type: ignore

    container.register(AIAgent, instance=ai_agent, scope=Scope.singleton)

    text_to_speech_service = GoogleTextToSpeechService(config.google_api_key)
    container.register(
        BaseTextToSpeechService, instance=text_to_speech_service,
    )

    chat_gateway = InMemoryChatGateway()
    container.register(ChatGateway, instance=chat_gateway)

    container.register(SoundService, MPG123SoundService, scope=Scope.transient)

    container.register(GenerateAIVoiceResponseCommandHandler)
    container.register(RequestSystemHelpCommandHandler)

    def init_mediator() -> Mediator:
        request_system_help_comand_handler = t.cast(
            RequestSystemHelpCommandHandler,
            container.resolve(RequestSystemHelpCommandHandler)
        )

        mediator = Mediator()
        mediator.register_handlers(RequestSystemHelpCommand, [request_system_help_comand_handler])
        return mediator

    container.register(Mediator, factory=lambda: init_mediator())

    return container
