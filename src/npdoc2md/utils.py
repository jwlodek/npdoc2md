import inspect
import os
from collections.abc import Callable
from logging import getLogger
from pathlib import Path
from types import ModuleType

logger = getLogger("npdoc2md")


def create_output_directory(output_path: Path) -> None:
    """Create the output directory if it does not exist.

    Parameters
    ----------
    output_path : Path
        The path to the output directory.

    Raises
    ------
    PermissionError
        If the output directory cannot be created due to permission issues.
    """

    output_path.mkdir(parents=True, exist_ok=True)
    logger.info(f"Created output directory at '{output_path}'.")


def validate_paths(input_path: Path, output_path: Path) -> None:
    """Validate the input and output paths.

    Checks if the input path exists and is readable, and if the output path is a directory that can be created or is writable.

    Raises
    ------
    FileNotFoundError
        If the input path does not exist.
    PermissionError
        If the input path is not readable or if the output path cannot be created or is not writable.
    NotADirectoryError
        If the output path exists but is a file instead of a directory.
    """

    if not input_path.exists():
        raise FileNotFoundError(f"Input path '{input_path}' does not exist.")
    elif not os.access(input_path, os.R_OK):
        raise PermissionError(f"Input path '{input_path}' is not readable.")
    elif input_path.is_file() and not input_path.suffix == ".py":
        raise ValueError(
            f"Input path '{input_path}' is a file but does not have a .py extension."
        )

    if output_path.is_file():
        raise NotADirectoryError(
            f"Output path '{output_path}' is a file, expected a directory."
        )
    elif not os.access(output_path, os.W_OK):
        raise PermissionError(f"Output path '{output_path}' is not writable.")


def get_target_output_file_path(
    input_file: Path, input_base_path: Path, output_base_path: Path
) -> Path:
    """Get the output file path for a given input file, preserving directory structure.

    Parameters
    ----------
    input_file : Path
        The path to the input Python file.
    input_base_path : Path
        The base path of the input files (used to determine relative paths).
    output_base_path : Path
        The base path for the output markdown files.

    Returns
    -------
    Path
        The path to the output markdown file.
    """

    # Get the relative path of the input file to the input base path
    relative_path = (
        input_file.relative_to(input_base_path)
        if input_base_path.is_dir()
        else Path(input_file.name)
    )

    # Construct the output file path by joining the output base path with the relative path
    output_file = output_base_path / relative_path.with_suffix(".md")

    return output_file


def get_cls_and_func_defined_in_module(
    module: ModuleType,
) -> tuple[dict[str, type], dict[str, Callable]]:
    """Get the sets of class and function names defined in a module."""
    classes = {
        name: obj
        for name, obj in inspect.getmembers(module, inspect.isclass)
        if obj.__module__ == module.__name__
    }
    functions = {
        name: obj
        for name, obj in inspect.getmembers(module, inspect.isfunction)
        if obj.__module__ == module.__name__
    }
    return classes, functions
