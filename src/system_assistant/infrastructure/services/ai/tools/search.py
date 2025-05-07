from langchain_community.tools import BraveSearch
from langchain_core.tools import BaseTool

from system_assistant.core.config import Config


def build_brave_search_tool(config: Config) -> BaseTool:
    tool = BraveSearch.from_api_key(config.brave_search_api_key, search_kwargs={'count': 3})
    return tool
