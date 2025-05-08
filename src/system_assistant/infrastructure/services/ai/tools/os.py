import os
from pathlib import Path

from langchain.tools import tool


def create_file(file_path: str, permission_level: int = 438) -> str:
    """
    Create a file by path.

    Args:
        file_path: absolute path of the new file (e.g. /home/user/new_file.txt).
        permission_level (optional): UNIX permissions level represented as number, default is 438.

    Returns:
        file_path: if file was created
    """

    path_obj = Path(file_path)
    path_obj.touch(permission_level)
    return file_path


def create_folder(
    folder_path: str,
    parents: bool = False,
    permission_level: int = 511,
):
    """
    Create folder by path

    Args:
        folder_path: absolute path to the new folder (e.g. /home/user/my_new_folder).
        parents (optional): if true create folders that don't exist on the path to the new folder.
        permission_level (optional): UNIX permissions level represented as number, default is 438.
    """

    path_obj = Path(folder_path)
    path_obj.mkdir(permission_level, parents)


def change_permissions(path: str, permission_level: int, recursive: bool = False):
    """
    Change permission of the file or folder

    Args:
        path: absolute path to the file or folder (e.g. /home/user/my_folder/my_file.pdf).
        permission_level: UNIX permission level represented as number (e.g. 777)
        recursive (optional): if path target is folder - changes permissions recursively
    """

    path_obj = Path(path)
    path_obj.chmod(permission_level)


def delete_file(path: str):
    """
    Delete file by provided path

    Args:
        path: absolute path to the file (e.g. /home/my_file.txt).
    """
    path_obj = Path(path)
    path_obj.unlink(missing_ok=True)


def delete_folder(path: str):
    """
    Delete folder by provided path

    Args:
        path: absolute path to the folder (e.g. /home/my_folder).
    """
    path_obj = Path(path)
    path_obj.rmdir()


def is_valid_path(path: str) -> bool:
    """
    Check if path is valid on current OS

    Args:
        path: absolute path that need to be checked (e.g. "/home/my_folder", "/usr/bin/my_bin")

    """
    return True if Path(path).exists() else False


def list_dir(path: str) -> list[str]:
    """
    List files and folders by path.

    Args:
        path: absolute path to the folder (e.g. /home/my_folder).

    Returns:
        list: list of files and directories (e.g. ['file1.txt', 'file2.txt', 'folder1', 'folder2']).
    """

    return os.listdir(path)


OS_TOOLS = [
    tool(f, parse_docstring=True) for f in (
        create_file,
        create_folder,
        change_permissions,
        list_dir,
        is_valid_path,
        delete_folder,
        delete_file,
    )
]
