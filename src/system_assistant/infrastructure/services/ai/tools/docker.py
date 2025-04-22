from typing import Any
import docker  # type: ignore[import-untyped]
from docker.models.containers import Container  # type: ignore[import-untyped]

from langchain.tools import tool

client = docker.from_env()


@tool(parse_docstring=True)
def list_containers() -> list[dict[str, Any]]:
    """
    List all running containers
    """

    containers: list[Container] = client.containers.list()
    return [{'name': c.name, 'id': c.id} for c in containers]


DOCKER_TOOLS = [list_containers]
