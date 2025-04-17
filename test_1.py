import typing as t

from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import Graph, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition
from pydantic import SecretStr

from system_assistant.core.config import Config
from system_assistant.core.container import init_container
from system_assistant.infrastructure.services.ai.gemini import (
    GEMINI_API_BASE_URL, GEMINI_MODEL)
from system_assistant.infrastructure.services.ai.deepseek import DEEPSEEK_BASE_URL, DEEPSEEK_CHAT_MODEL
from langgraph.checkpoint.memory import MemorySaver


memory = MemorySaver()
container = init_container()
config = t.cast(Config, container.resolve(Config))


class State(t.TypedDict, total=True):
    messages: t.Annotated[list, add_messages]


def draw_graph():
    try:
        with open('graph.png', '+wb') as file:
            file.write(graph.get_graph().draw_mermaid_png())
    except Exception as e:
        print(e)
        # This requires some extra dependencies and is optional
        pass


@tool(parse_docstring=True)
def get_db_tables() -> list[str]:
    """
    Function that returns db tables
    """
    return ['users', 'articles', 'messages']


def chatbot(state: State):
    return {'messages': [llm.invoke(state['messages'])]}


# _llm = ChatOpenAI(
#     model=GEMINI_MODEL, base_url=GEMINI_API_BASE_URL, api_key=SecretStr(config.gemini_api_key)
# )
_llm = ChatOpenAI(
    model=DEEPSEEK_CHAT_MODEL, base_url=DEEPSEEK_BASE_URL, api_key=SecretStr(config.deepseek_api_key)
)
llm = _llm.bind_tools([get_db_tables])

graph_builder = StateGraph(State)

graph_builder.add_node('chatbot', chatbot)

tool_node = ToolNode(tools=[get_db_tables])
graph_builder.add_node('tools', tool_node)

graph_builder.add_conditional_edges('chatbot', tools_condition)

graph_builder.add_edge('tools', 'chatbot')
graph_builder.set_entry_point('chatbot')

graph = graph_builder.compile(checkpointer=memory)
draw_graph()

config = {"configurable": {"thread_id": "1"}}


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,  # type: ignore
        stream_mode='values',
    ):
        event['messages'][-1].pretty_print()


while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except Exception as e:
        print(e)
        # fallback if input() is not available
        user_input = "What do you know about LangGraph?"
        print("User: " + user_input)
        stream_graph_updates(user_input)
        break
