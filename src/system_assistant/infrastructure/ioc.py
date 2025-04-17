import typing as t
from functools import cache

from langgraph.checkpoint.memory import MemorySaver
from punq import Container, Scope  # type: ignore[import-untyped]

from system_assistant.application.commands.generate_ai_voice_response import (
    GenerateAIVoiceResponseCommand, GenerateAIVoiceResponseCommandHandler)
from system_assistant.application.commands.request_system_help import (
    RequestSystemHelpCommand, RequestSystemHelpCommandHandler)
from system_assistant.application.gateways.chat import ChatGateway, FakeChatGateway
from system_assistant.application.mediator import Mediator
from system_assistant.application.services.ai.base import (LLM,  # noqa
                                                           AIAgent, FakeAIAgent, FakeLLM)
from system_assistant.application.services.text_to_speech.base import \
    BaseTextToSpeechService
from system_assistant.core.config import Config
from system_assistant.infrastructure.services.ai.deepseek import \
    DeepSeek  # noqa
from system_assistant.infrastructure.services.ai.gemini import Gemini  # noqa
from system_assistant.infrastructure.services.ai.openai_agent import \
    ReactOpenAIAgent
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

    ai_agent = ReactOpenAIAgent(config, memory_saver=MemorySaver(), tools=TOOLS)
    if llm_type == 'gemini':
        llm: LLM = Gemini(config.gemini_api_key)
        container.register(Gemini, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm, )
        ai_agent.init_gemini_react_agent()
    elif llm_type == 'deepseek':
        llm = DeepSeek(config.deepseek_api_key)
        container.register(DeepSeek, instance=llm, scope=Scope.singleton)
        container.register(LLM, instance=llm)
        ai_agent.init_deepseek_react_agent()
    elif llm_type == 'fake':
        llm = FakeLLM()
        container.register(LLM, FakeLLM)
        ai_agent = FakeAIAgent()  # type: ignore

    container.register(AIAgent, instance=ai_agent, scope=Scope.singleton)

    text_to_speech_service = GoogleTextToSpeechService(config.google_api_key)
    container.register(
        BaseTextToSpeechService, instance=text_to_speech_service,
    )

    chat_gateway = FakeChatGateway()
    container.register(ChatGateway, instance=chat_gateway)

    container.register(SoundService, MPG123SoundService, scope=Scope.transient)

    def init_mediator() -> Mediator:
        mediator = Mediator(
            command_handlers={
                GenerateAIVoiceResponseCommand: [
                        GenerateAIVoiceResponseCommandHandler(text_to_speech_service, llm)
                ],
                RequestSystemHelpCommand: [
                    RequestSystemHelpCommandHandler(
                        chat_gateway=chat_gateway, ai_agent=ai_agent,  # type: ignore
                    )
                ],
            }
        )
        return mediator

    container.register(Mediator, factory=lambda: init_mediator())

    return container
