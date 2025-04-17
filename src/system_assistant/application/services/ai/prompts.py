import os
from pathlib import Path
import platform

from system_assistant.core import ROOT


_SYSTEM_ASSISTANT_PROMPT = """
You are built-in OS assistant that helps user with usage of his OS

Context:
    OS: {os}
    Distribution: {distribution}
    Current working directory: {current_dir}
    Directory list: {directory_list}

Important:
    If you are using provided tools that require path in their parameters ALWAYS pass this path
"""


def construct_system_assistant_prompt(
    operating_system: str | None = None,
    distribution: str | None = None,
    current_dir: Path | None = None,
    directory_list: list[str] | None = None,
) -> str:
    operating_system = operating_system or platform.system()
    distribution = distribution or platform.freedesktop_os_release()['NAME']
    current_dir = current_dir or ROOT
    directory_list = directory_list or os.listdir()
    return _SYSTEM_ASSISTANT_PROMPT.format_map({
        'os': operating_system,
        'distribution': distribution,
        'current_dir': current_dir,
        'directory_list': directory_list
    })
