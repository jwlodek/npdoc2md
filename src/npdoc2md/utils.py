import inspect
import os
from collections.abc import Callable, Mapping
from logging import getLogger
from pathlib import Path
from types import ModuleType
from typing import Final

logger = getLogger("npdoc2md")


# Note: The following mapping is vendored from sphix-doc/sphinx:
# https://github.com/sphinx-doc/sphinx/blob/cc7c6f435ad37bb12264f8118c8461b230e6830c/sphinx/util/typing.py#L50
_INVALID_BUILTIN_CLASSES: Final[Mapping[tuple[str, str], str]] = {
    # types from 'contextvars'
    ("_contextvars", "Context"): "contextvars.Context",
    ("_contextvars", "ContextVar"): "contextvars.ContextVar",
    ("_contextvars", "Token"): "contextvars.Token",
    # types from 'ctypes':
    ("_ctypes", "Array"): "ctypes.Array",
    ("_ctypes", "Structure"): "ctypes.Structure",
    ("_ctypes", "Union"): "ctypes.Union",
    # types from 'io':
    ("_io", "BufferedRandom"): "io.BufferedRandom",
    ("_io", "BufferedReader"): "io.BufferedReader",
    ("_io", "BufferedRWPair"): "io.BufferedRWPair",
    ("_io", "BufferedWriter"): "io.BufferedWriter",
    ("_io", "BytesIO"): "io.BytesIO",
    ("_io", "FileIO"): "io.FileIO",
    ("_io", "StringIO"): "io.StringIO",
    ("_io", "TextIOWrapper"): "io.TextIOWrapper",
    # types from 'json':
    ("json.decoder", "JSONDecoder"): "json.JSONDecoder",
    ("json.encoder", "JSONEncoder"): "json.JSONEncoder",
    # types from 'lzma':
    ("_lzma", "LZMACompressor"): "lzma.LZMACompressor",
    ("_lzma", "LZMADecompressor"): "lzma.LZMADecompressor",
    # types from 'multiprocessing':
    ("multiprocessing.context", "Process"): "multiprocessing.Process",
    # types from 'pathlib':
    ("pathlib._local", "Path"): "pathlib.Path",
    ("pathlib._local", "PosixPath"): "pathlib.PosixPath",
    ("pathlib._local", "PurePath"): "pathlib.PurePath",
    ("pathlib._local", "PurePosixPath"): "pathlib.PurePosixPath",
    ("pathlib._local", "PureWindowsPath"): "pathlib.PureWindowsPath",
    ("pathlib._local", "WindowsPath"): "pathlib.WindowsPath",
    # types from 'pickle':
    ("_pickle", "Pickler"): "pickle.Pickler",
    ("_pickle", "Unpickler"): "pickle.Unpickler",
    # types from 'struct':
    ("_struct", "Struct"): "struct.Struct",
    # types from 'types':
    ("builtins", "async_generator"): "types.AsyncGeneratorType",
    ("builtins", "builtin_function_or_method"): "types.BuiltinMethodType",
    ("builtins", "cell"): "types.CellType",
    ("builtins", "classmethod_descriptor"): "types.ClassMethodDescriptorType",
    ("builtins", "code"): "types.CodeType",
    ("builtins", "coroutine"): "types.CoroutineType",
    ("builtins", "ellipsis"): "types.EllipsisType",
    ("builtins", "frame"): "types.FrameType",
    ("builtins", "function"): "types.LambdaType",
    ("builtins", "generator"): "types.GeneratorType",
    ("builtins", "getset_descriptor"): "types.GetSetDescriptorType",
    ("builtins", "mappingproxy"): "types.MappingProxyType",
    ("builtins", "member_descriptor"): "types.MemberDescriptorType",
    ("builtins", "method"): "types.MethodType",
    ("builtins", "method-wrapper"): "types.MethodWrapperType",
    ("builtins", "method_descriptor"): "types.MethodDescriptorType",
    ("builtins", "module"): "types.ModuleType",
    ("builtins", "NoneType"): "types.NoneType",
    ("builtins", "NotImplementedType"): "types.NotImplementedType",
    ("builtins", "traceback"): "types.TracebackType",
    ("builtins", "wrapper_descriptor"): "types.WrapperDescriptorType",
    # types from 'weakref':
    ("_weakrefset", "WeakSet"): "weakref.WeakSet",
    # types from 'zipfile':
    ("zipfile._path", "CompleteDirs"): "zipfile.CompleteDirs",
    ("zipfile._path", "Path"): "zipfile.Path",
}


def sanitize_signature(signature: str) -> str:
    """Sanitize a signature by replacing invalid types with their correct names.

    This is necessary because some types are represented in the signature
    as their internal names (e.g., '_io.BytesIO' instead of 'io.BytesIO'),
    which can be confusing. This function uses a predefined mapping to replace these
    invalid type representations with their correct, fully qualified names.

    Parameters
    ----------
    signature : str
        The original function or method signature to sanitize.

    Returns
    -------
    str
        The sanitized signature with invalid types replaced by their correct names.
    """

    for (module_name, type_name), correct_type in _INVALID_BUILTIN_CLASSES.items():
        invalid_type = f"{module_name}.{type_name}"
        if invalid_type in signature:
            signature = signature.replace(invalid_type, correct_type)

    return signature


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

    Checks if the input path exists and is readable, and if the output path
    is a directory that can be created or is writable.

    Raises
    ------
    FileNotFoundError
        If the input path does not exist.
    PermissionError
        If the input/output paths are not readable/writable.
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

    # Build the output file path by joining the output base path with the rel path
    output_file = output_base_path / relative_path.with_suffix(".md")

    return output_file


def get_cls_and_func_defined_in_module(
    module: ModuleType,
) -> tuple[dict[str, type], dict[str, Callable]]:
    """Get the sets of class and function names defined in a module.

    Parameters
    ----------
    module : ModuleType
        The module to inspect.

    Returns
    -------
    tuple[dict[str, type], dict[str, Callable]]
        A tuple containing two dictionaries: the first maps class names to class
        objects, and the second maps function names to function objects, for all
        classes and functions defined in the given module.
    """
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
