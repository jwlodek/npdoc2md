"""Module for converting docstrings in Python files to markdown format.

This module defines the main functionality for the npdoc2md package, which includes:
- Classes for docstring elements (ModuleElement, ClassElement, FunctionDocstring)
- A helper func for converting docstring meta information to markdown tables
- The main func npdoc2md that orchestrates the conversion of docstrings to markdown
"""

# Some standard lib imports
import importlib
import inspect
import logging
from pathlib import Path
from types import ModuleType
from typing import Protocol, TypeVar, runtime_checkable

# Import typing to use python3 typing features
from docstring_parser import (
    Docstring,
    DocstringDeprecated,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
    Style,
    parse,
)
from docstring_parser.common import DocstringExample

from .utils import get_cls_and_func_defined_in_module, get_target_output_file_path

logger = logging.getLogger("npdoc2md")


@runtime_checkable
class DocToMarkdownElementProtocol(Protocol):
    name: str
    docstring: Docstring
    signature: str
    level: int


TableItem = DocstringMeta | DocToMarkdownElementProtocol

TableItemT = TypeVar("TableItemT", bound=TableItem)


def docstring_metas_to_md_table(name: str, level: int, meta: list[TableItemT]) -> str:
    """Helper function to convert docstring meta to markdown table

    Parameters
    ----------
    name : str
        Name of the docstring meta (ex: Parameters, Returns, Raises)
    level : int
        Heading level for the markdown table
    meta : list[DocstringMetaT]
        List of docstring meta items to include in the table

    Returns
    -------
    str
        Markdown table representation of the docstring meta items
    """

    if len(meta) == 0:
        logger.warning(f"No items provided for {name} meta. Skipping table generation.")
        return ""

    meta_type = type(meta[0])
    if not all(isinstance(item, meta_type) for item in meta):
        raise ValueError("All items in meta list must be of the same type")

    logger.debug(f"Generating markdown table listing {len(meta)} {name}")

    # ruff: disable[E501]
    header = ""
    if meta_type == DocstringParam:
        header = f"{'#' * level} {name}\n{' | '.join([name[:-1], 'Type', 'Optional', 'Default', 'Description'])}\n{' | '.join(['---'] * 5)}\n"
    elif meta_type == DocstringReturns:
        header = f"{'#' * level} {name}\n{' | '.join(['Type', 'Variable Name', 'Is Generator', 'Description'])}\n{' | '.join(['---'] * 4)}\n"
    elif meta_type == DocstringRaises:
        header = f"{'#' * level} {name}\n{' | '.join(['Error', 'Description'])}\n{' | '.join(['---'] * 2)}\n"
    elif meta_type == DocstringDeprecated:
        header = f"{'#' * level} {name}\n{' | '.join(['Version', 'Description'])}\n{' | '.join(['---'] * 2)}\n"
    elif meta_type == DocstringExample:
        header = f"{'#' * level} {name}\n{' | '.join(['Snippet', 'Description'])}\n{' | '.join(['---'] * 2)}\n"
    # Cannot use issubclass w/ DocstringElementProtocol since it's a protocol w/ non-method members
    elif isinstance(meta[0], DocToMarkdownElementProtocol):
        header = f"{'#' * level} {name}\n{' | '.join([name[:-1], 'Description'])}\n{' | '.join(['---'] * 2)}\n"
    else:
        raise NotImplementedError(f"Unsupported TableItem type {meta_type}")

    table = header
    for item in meta:
        if isinstance(item, DocstringParam):
            table += f"{item.arg_name} | {item.type_name} | {item.is_optional} | {item.default if item.is_optional else 'N/A'} | {item.description}\n"
        elif isinstance(item, DocstringReturns):
            table += f"{item.type_name} | {item.return_name if item.return_name is not None else 'N/A'} | {item.is_generator} | {item.description}\n"
        elif isinstance(item, DocstringRaises):
            table += f"{item.type_name} | {item.description}\n"
        elif isinstance(item, DocstringDeprecated):
            table += f"{item.version} | {item.description}\n"
        elif isinstance(item, DocstringExample):
            table += f"{item.snippet} | {item.description}\n"
        elif isinstance(item, DocToMarkdownElementProtocol):
            table += f"[{item.name}](#{item.name}) | {item.docstring.short_description if item.docstring.short_description is not None else 'N/A'}\n"

    # ruff: enable[E501]

    return table


class DocToMarkdownElement(DocToMarkdownElementProtocol):
    """Base class for elements that can be included in the markdown docs.

    Attributes
    ----------
    name : str
        Name of the element (ex: function name, class name)
    docstring : Docstring
        Parsed docstring object for the element
    signature : str
        Signature of the element (ex: function signature)
    level : int
        Heading level for the element in the markdown documentation.
        For example, 1 for module, 2 for class, 3 for method.

    """

    name: str
    docstring: Docstring
    signature: str | None = (
        None  # Signature is optional since modules may not have a signature
    )
    level: int

    def __init__(
        self, name: str, docstring: Docstring, level: int, signature: str | None = None
    ):
        """Initialize the element with its name, docstring, signature, and heading.

        Parameters
        ----------
        name : str
            Name of the element (ex: function name, class name)
        signature : str, optional
            Signature of the element (ex: function signature)
        docstring : Docstring
            Parsed docstring object for the element
        level : int
            Heading level for the element in the markdown documentation.
            For example, 1 for module, 2 for class, 3 for method.
        """
        self.name = name
        self.signature = signature
        self.docstring = docstring
        self.level = level

    def __repr__(self) -> str:
        """String representation of the element in markdown format.

        Returns
        -------
        str
            Markdown representation of the element.
        """

        repr = f"{'#' * self.level} {self.name}\n"
        repr += (
            f"```Python\n{self.signature}\n```\n" if self.signature is not None else ""
        )
        repr += (
            f"{self.docstring.description}\n"
            if self.docstring.description is not None
            else ""
        )

        # Class docstrings will include attributes instead of parameters.
        param_header = (
            "Parameters" if not isinstance(self, ClassElement) else "Attributes"
        )
        if len(self.docstring.params) > 0:
            repr += docstring_metas_to_md_table(
                param_header, self.level + 1, self.docstring.params
            )

        if self.docstring.returns is not None:
            repr += docstring_metas_to_md_table(
                "Returns", self.level + 1, [self.docstring.returns]
            )

        if len(self.docstring.raises) > 0:
            repr += docstring_metas_to_md_table(
                "Raises", self.level + 1, self.docstring.raises
            )

        if len(self.docstring.examples) > 0:
            repr += docstring_metas_to_md_table(
                "Examples", self.level + 1, self.docstring.examples
            )

        for subc in ["classes", "functions", "methods"]:
            if hasattr(self, subc) and len(getattr(self, subc)) > 0:
                repr += docstring_metas_to_md_table(
                    subc.capitalize(), self.level + 1, getattr(self, subc)
                )

        for subc in ["classes", "functions", "methods"]:
            if hasattr(self, subc):
                for element in getattr(self, subc):
                    repr += f"\n{element.__repr__()}"

        return repr


class FunctionElement(DocToMarkdownElement):
    """Class for representing function docstrings."""

    ...


class ClassElement(DocToMarkdownElement):
    """Representation of class docstrings, which can contain methods as sub-elements.

    Attributes
    ----------
    methods : list[FunctionElement]
        List of methods defined in the class, represented as FunctionElement objects.
    """

    methods: list[FunctionElement]

    def __init__(self, cls: type, include_private: bool = False):
        """Initialize a class's docstring representation.

        Includes the class's name, signature, docstring, and heading.

        Parameters
        ----------
        cls : type
            The class to parse for docstrings and sub-elements
        include_private : bool, default=False
            Whether to include private members in the documentation.
        """

        bases = ", ".join(base_cls.__name__ for base_cls in cls.__bases__)
        signature = (
            f"class {cls.__name__}({bases})"
            if len(cls.__bases__) > 0
            else f"class {cls.__name__}"
        )
        super().__init__(
            name=cls.__name__,
            signature=signature,
            docstring=parse(
                cls.__doc__
                if cls.__doc__ is not None
                else f"Description for {cls.__name__}",
                style=Style.NUMPYDOC,
            ),
            level=2,
        )

        target_methods = {
            method_name: method
            for method_name, method in cls.__dict__.items()
            if inspect.isfunction(method)
            or inspect.ismethod(method)
            and (include_private or not method_name.startswith("_"))
        }
        self.methods = [
            FunctionElement(
                name=method_name,
                signature=f"def {method_name}{str(inspect.signature(method))}",
                docstring=parse(
                    getattr(cls, method_name).__doc__
                    if getattr(cls, method_name).__doc__ is not None
                    else f"Description for {method_name}()",
                    style=Style.NUMPYDOC,
                ),
                level=3,
            )
            for method_name, method in target_methods.items()
        ]


class ModuleElement(DocToMarkdownElement):
    """Representation of module docstrings, contain classes and funcs as sub-elements.

    Attributes
    ----------
    classes : list[ClassElement]
        List of classes defined in the module, represented as ClassElement objects
    functions : list[FunctionDocstring]
        List of funcs defined in the module, represented as FunctionDocstring objects
    """

    classes: list[ClassElement]
    functions: list[FunctionElement]

    def __init__(self, module: ModuleType, include_private: bool = False):
        """Initialize the ModuleElement with the module's name, docstring, and heading.

        Also parses the classes and functions defined in the module as sub-elements.

        Parameters
        ----------
        module : ModuleType
            The module to parse for docstrings and sub-elements
        include_private : bool, default False
            Whether to include private members in the documentation.
        """

        super().__init__(
            name=module.__name__,
            signature=None,
            docstring=parse(
                module.__doc__
                if module.__doc__ is not None
                else f"Description for {module.__name__} module",
                style=Style.NUMPYDOC,
            ),
            level=1,
        )

        all_classes, all_functions = get_cls_and_func_defined_in_module(module)

        self.classes = [
            ClassElement(cls=cls, include_private=include_private)
            for cls in all_classes.values()
        ]

        self.functions = [
            FunctionElement(
                name=func_name,
                signature=f"def {func_name}{str(inspect.signature(func))}",
                docstring=parse(
                    getattr(module, func_name).__doc__
                    if getattr(module, func_name).__doc__ is not None
                    else f"Description for {func_name}()",
                    style=Style.NUMPYDOC,
                ),
                level=2,
            )
            for func_name, func in all_functions.items()
        ]


def get_target_python_files(input_path: Path, ignore_private: bool) -> list[Path]:
    """Helper function to get list of target python files to process

    Parameters
    ----------
    input_path : Path
        Path to the input file or directory containing files to parse
    ignore_private : bool
        Whether to ignore private members (those starting with an underscore)

    Returns
    -------
    List[Path]
        List of paths to target python files to process
    """

    all_src_files: list[Path] = []

    # Find all python files at the input path
    if input_path.is_file():
        all_src_files.append(input_path)
    else:
        for file_path in input_path.glob("**/*.py"):
            if file_path.is_file():
                all_src_files.append(file_path)

    if ignore_private:
        src_files = []
        for file in all_src_files:
            if file.name.startswith("_") and file.name != "__init__.py":
                logger.info(f"Ignoring private file {file.name}")
            else:
                src_files.append(file)
        return src_files
    else:
        return all_src_files


def npdoc2md(
    input_path: Path, output_path: Path, ignore_private: bool = False
) -> dict[Path, str]:
    """Main function for converting docstrings to markdown

    This function orchestrates the process of converting docstrings in Python files
    to markdown format. It identifies the target Python files, imports them to
    access their docstrings, and then parses the docstrings to generate markdown docs.

    Parameters
    ----------
    input_path : Path
        Path to the input file or directory containing files to parse
    output_path : Path
        Path to the output directory where markdown files will be saved
    ignore_private : bool, optional
        Whether to ignore private members, by default False
    """

    src_files = get_target_python_files(input_path, ignore_private)
    output_files: dict[Path, str] = {}

    for src_file in src_files:
        # Import the module to access its docstrings
        module_name = (
            src_file.stem if src_file.name != "__init__.py" else src_file.parent.stem
        )
        logger.info(f"Processing file {src_file} as module {module_name}")
        module = importlib.import_module(
            f".{module_name}", package=input_path.stem if input_path.is_dir() else None
        )

        output_file_path = get_target_output_file_path(
            src_file, input_path, output_path
        )
        md_text = ModuleElement(module, include_private=ignore_private).__repr__()
        output_files[output_file_path] = md_text

    return output_files
