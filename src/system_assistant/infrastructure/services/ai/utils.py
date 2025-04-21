from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

from system_assistant.domain.vo import Message


def to_langchain_message(message: Message) -> BaseMessage:
    if message.sender == 'user':
        return HumanMessage(content=message.content)
    elif message.sender == 'assistant':
        return SystemMessage(content=message.content)
    raise TypeError
