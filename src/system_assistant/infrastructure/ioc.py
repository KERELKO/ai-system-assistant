import typing as t

from langchain.tools import BaseTool
from punq import (  # type: ignore[import-untyped]
    Container,
    Scope,
)
from system_assistant.application.commands.request_system_help import (
    RequestSystemHelpCommand,
    RequestSystemHelpCommandHandler,
)
from system_assistant.application.gateways.chat import (
    ChatGateway,
    InMemoryChatGateway,
)
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import LLM  # noqa
from system_assistant.application.services.ai.base import (
    AIAgent,
    FakeAIAgent,
    FakeLLM,
)
from system_assistant.application.services.text_to_speech.base import BaseTextToSpeechService
from system_assistant.core.config import Config
from system_assistant.infrastructure.db.sqlite.init import get_engine
from system_assistant.infrastructure.gateways.chat.sqlite import SQLiteChatGateway
from system_assistant.infrastructure.services.ai.deepseek import (  # noqa
    DeepSeek,
    DeepSeekOpenAIAgent,
)
from system_assistant.infrastructure.services.ai.gemini import (  # noqa
    Gemini,
    GeminiOpenAIAgent,
)
from system_assistant.infrastructure.services.ai.openai_agent import BaseReactOpenAIAgent
from system_assistant.infrastructure.services.sound.base import SoundService
from system_assistant.infrastructure.services.sound.mpg123 import MPG123SoundService
from system_assistant.infrastructure.services.text_to_speech.google import GoogleTextToSpeechService


def register_llm(
    container: Container,
    llm_type: str = 'fake',
    llm_tools: list[BaseTool] | None = None,
    llm_temperature: float = 1.0,
) -> Container:

    llm_tools = llm_tools or []

    config = t.cast(Config, container.resolve(Config))

    if llm_type == 'gemini':
        ai_agent: BaseReactOpenAIAgent = GeminiOpenAIAgent(
            config, tools=llm_tools, temperature=llm_temperature,
        )
        llm: LLM = Gemini(config.gemini_api_key)
        container.register(Gemini, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)

    elif llm_type == 'deepseek':
        ai_agent = DeepSeekOpenAIAgent(
            config, tools=llm_tools, temperature=llm_temperature,
        )
        llm = DeepSeek(config.deepseek_api_key)
        container.register(DeepSeek, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)

    elif llm_type == 'fake':
        llm = FakeLLM()
        container.register(LLM, FakeLLM)
        ai_agent = FakeAIAgent()  # type: ignore

    else:
        raise ValueError(f'Unsupported LLM: {llm_type}')

    container.register(AIAgent, instance=ai_agent, scope=Scope.singleton)  # type: ignore
    return container


def register_mediator_handlers(container: Container) -> Container:
    container.register(RequestSystemHelpCommandHandler)

    return container


def register_gateway(container: Container, storage: str) -> Container:
    config = t.cast(Config, container.resolve(Config))

    if storage == 'memory':
        container.register(ChatGateway, factory=InMemoryChatGateway)
    elif storage == 'sqlite':
        engine = get_engine(config)
        container.register(ChatGateway, instance=SQLiteChatGateway(engine), scope=Scope.singleton)
    else:
        raise ValueError(f'Unsupported storage: {storage}')

    return container


def register_services(container: Container) -> Container:
    config = t.cast(Config, container.resolve(Config))
    container.register(
        BaseTextToSpeechService, instance=GoogleTextToSpeechService(config.google_api_key),
    )
    container.register(SoundService, MPG123SoundService, scope=Scope.transient)
    return container


def register_mediator(container: Container) -> Container:
    request_system_help_comand_handler = t.cast(
        RequestSystemHelpCommandHandler,
        container.resolve(RequestSystemHelpCommandHandler)
    )

    mediator = Mediator()
    mediator.register_handlers(RequestSystemHelpCommand, [request_system_help_comand_handler])

    container.register(Mediator, instance=mediator, scope=Scope.singleton)
    return container


def init_base_container() -> Container:
    """Function to initialize DI container"""

    container = Container()

    config = Config()
    container.register(Config, instance=config, scope=Scope.singleton)

    return container
