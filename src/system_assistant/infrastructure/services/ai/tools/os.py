from pathlib import Path

from langchain.tools import tool


@tool(parse_docstring=True)
def create_file(file_path: str, permission_level: int = 438):
    """
    Create a file by path.

    Args:
        file_path: absolute path of the new file (e.g. /home/user/new_file.txt).
        permission_level (optional): UNIX permissions level represented as number, default is 438.
    """

    path_obj = Path(file_path)
    path_obj.touch(permission_level)


@tool(parse_docstring=True)
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


@tool(parse_docstring=True)
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
