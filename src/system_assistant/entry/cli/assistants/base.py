from abc import abstractmethod
from dataclasses import dataclass

from system_assistant.application.mediator import Mediator
from system_assistant.core.types import LLMConfiguration, SystemContext


@dataclass(eq=False, slots=True)
class Context:
    system_context: SystemContext
    llm_conf: LLMConfiguration
    debug: bool
    chat_id: str | None


@dataclass(eq=False, repr=False, slots=True)
class BaseSystemAssistant:
    mediator: Mediator
    context: Context

    @abstractmethod
    async def run(self):
        ...
