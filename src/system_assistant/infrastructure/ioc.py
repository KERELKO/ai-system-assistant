from dataclasses import dataclass
import typing as t
from functools import cache

from punq import Container, Scope  # type: ignore[import-untyped]
from langchain.tools import BaseTool

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
from system_assistant.infrastructure.services.ai.tools.docker import DOCKER_TOOLS
from system_assistant.infrastructure.services.ai.tools.os import OS_TOOLS
from system_assistant.infrastructure.services.sound.base import SoundService
from system_assistant.infrastructure.services.sound.mpg123 import \
    MPG123SoundService
from system_assistant.infrastructure.services.text_to_speech.google import \
    GoogleTextToSpeechService


@dataclass(frozen=True, repr=True, slots=True, eq=True)
class ContainerConfiguration:
    llm: t.Literal['deepseek', 'gemini', 'fake']
    llm_tools: tuple[str, ...]
    llm_temperature: float


def _register_llm(container: Container, configuration: ContainerConfiguration) -> Container:

    config = t.cast(Config, container.resolve(Config))
    tools: list[BaseTool] = []

    if 'os' in (ct := configuration.llm_tools):
        tools.extend(OS_TOOLS)
    if 'docker' in ct:
        tools.extend(DOCKER_TOOLS)

    if configuration.llm == 'gemini':
        ai_agent: BaseReactOpenAIAgent = GeminiOpenAIAgent(
            config, tools=tools, temperature=configuration.llm_temperature,
        )
        llm: LLM = Gemini(config.gemini_api_key)
        container.register(Gemini, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)

    elif configuration.llm == 'deepseek':
        ai_agent = DeepSeekOpenAIAgent(
            config, tools=tools, temperature=configuration.llm_temperature,
        )
        llm = DeepSeek(config.deepseek_api_key)
        container.register(DeepSeek, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)

    elif configuration.llm == 'fake':
        llm = FakeLLM()
        container.register(LLM, FakeLLM)
        ai_agent = FakeAIAgent()  # type: ignore

    container.register(AIAgent, instance=ai_agent, scope=Scope.singleton)  # type: ignore
    return container


def _register_mediator(container: Container) -> Container:
    request_system_help_comand_handler = t.cast(
        RequestSystemHelpCommandHandler,
        container.resolve(RequestSystemHelpCommandHandler)
    )

    mediator = Mediator()
    mediator.register_handlers(RequestSystemHelpCommand, [request_system_help_comand_handler])

    container.register(Mediator, instance=mediator, scope=Scope.singleton)
    return container


@cache
def init_container(configuration: ContainerConfiguration) -> Container:
    """Function to initialize DI container"""

    container = Container()

    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    _register_llm(container, configuration)

    text_to_speech_service = GoogleTextToSpeechService(config.google_api_key)
    container.register(
        BaseTextToSpeechService, instance=text_to_speech_service,
    )

    container.register(ChatGateway, factory=InMemoryChatGateway)

    container.register(SoundService, MPG123SoundService, scope=Scope.transient)

    container.register(GenerateAIVoiceResponseCommandHandler)
    container.register(RequestSystemHelpCommandHandler)

    _register_mediator(container)

    return container
