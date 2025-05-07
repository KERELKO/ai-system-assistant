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


def run_container(path: str) -> dict[str, Any]:
    """
    Run container located by `path` where destination is Dockerfile

    Args:
        path: absolute path to Dockerfile (e.g. /my_path/my_project/Dockerfile)
    """
    return {}


DOCKER_TOOLS = [list_containers]
