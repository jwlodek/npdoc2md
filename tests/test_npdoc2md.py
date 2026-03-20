import pytest
from docstring_parser import Docstring, Style, parse
from docstring_parser.common import (
    DocstringDeprecated,
    DocstringExample,
    DocstringMeta,
    DocstringParam,
    DocstringRaises,
    DocstringReturns,
)

from npdoc2md.npdoc2md import (
    ClassElement,
    DocToMarkdownElement,
    docstring_metas_to_md_table,
    get_target_python_files,
)


@pytest.mark.parametrize(
    "ignore_private, expected_files",
    [
        (False, {"file1.py", "__init__.py", "subdir/file4.py", "_file5.py"}),
        (True, {"file1.py", "__init__.py", "subdir/file4.py"}),
    ],
)
def test_get_target_python_files(tmp_path, ignore_private, expected_files):
    # Create a temporary directory with some Python files and other files
    dir_path = tmp_path / "test_dir"
    dir_path.mkdir()
    (dir_path / "file1.py").touch()
    (
        dir_path / "__init__.py"
    ).touch()  # __init__.py should be included as it's not a private file
    (dir_path / "file3.txt").touch()  # Non-Python file
    (dir_path / "subdir").mkdir()
    (dir_path / "subdir" / "file4.py").touch()
    (dir_path / "_file5.py").touch()  # Private file

    # Test that get_target_python_files returns only .py files
    python_files = get_target_python_files(dir_path, ignore_private)
    expected_files = {dir_path / file for file in expected_files}
    assert set(python_files) == expected_files


def test_docstring_metas_to_md_table_empty():
    result = docstring_metas_to_md_table("Parameters", 2, [])
    assert result == ""


def test_docstring_metas_to_md_table_invalid_type():
    with pytest.raises(ValueError):
        docstring_metas_to_md_table(
            "Metas",
            2,
            [
                DocstringDeprecated([], "Deprecated", "1.0"),
                DocstringReturns([], "Returns something", "int", False, "result"),
            ],
        )


@pytest.mark.parametrize(
    "optional, default, expected_default",
    [
        (True, "42", "42"),
        (True, None, "None"),
        (False, "42", "N/A"),
        (False, None, "N/A"),
    ],
)
def test_docstring_metas_to_md_table_param_meta(optional, default, expected_default):
    param_meta = [
        DocstringParam(
            [], "Description for param1", "param1", "int", optional, default
        ),
    ]
    result = docstring_metas_to_md_table("Parameters", 2, param_meta)
    expected = f"""## Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
param1 | int | {optional} | {expected_default} | Description for param1
"""
    assert result == expected


@pytest.mark.parametrize("is_generator", [True, False])
def test_docstring_metas_to_md_table_returns_meta(is_generator):
    returns_meta = [
        DocstringReturns(
            [], "Description for return value", "int", is_generator, "result"
        ),
    ]
    result = docstring_metas_to_md_table("Returns", 2, returns_meta)
    expected = f"""## Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
int | result | {is_generator} | Description for return value
"""
    assert result == expected


def test_docstring_metas_to_md_table_raises_meta():
    raises_meta = [
        DocstringRaises([], "Description for ValueError", "ValueError"),
    ]
    result = docstring_metas_to_md_table("Raises", 2, raises_meta)
    expected = """## Raises
Error | Description
--- | ---
ValueError | Description for ValueError
"""
    assert result == expected


def test_docstring_metas_to_md_table_deprecated_meta():
    deprecated_meta = [
        DocstringDeprecated([], "This function is deprecated", "1.0"),
    ]
    result = docstring_metas_to_md_table("Deprecated", 2, deprecated_meta)
    expected = """## Deprecated
Version | Description
--- | ---
1.0 | This function is deprecated
"""
    assert result == expected


def test_docstring_metas_to_md_table_example_meta():
    example_meta = [
        DocstringExample([], "This is an example snippet", "Example code snippet"),
    ]
    result = docstring_metas_to_md_table("Example", 2, example_meta)
    expected = """## Example
Snippet | Description
--- | ---
This is an example snippet | Example code snippet
"""
    assert result == expected


def test_docstring_metas_to_md_table_element_protocol_meta():
    element_meta = [
        DocToMarkdownElement(
            name="TestElement",
            signature="def test_element()",
            docstring=parse("Short description of TestElement.", style=Style.NUMPYDOC),
            level=2,
        )
    ]
    result = docstring_metas_to_md_table("Elements", 2, element_meta)
    expected = """## Elements
Element | Description
--- | ---
[TestElement](#TestElement) | Short description of TestElement.
"""
    assert result == expected


def test_docstring_metas_to_table_multiple_metas():
    multiple_metas: list[DocstringMeta] = [
        DocstringParam(
            ["param"], "Description for param1", "param1", "int", True, "42"
        ),
        DocstringParam(
            ["param"], "Description for param2", "param2", "str", False, "test"
        ),
    ]
    docstring = Docstring(style=Style.NUMPYDOC)
    docstring.meta = multiple_metas
    result = docstring_metas_to_md_table("Parameters", 2, multiple_metas)
    expected = """## Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
param1 | int | True | 42 | Description for param1
param2 | str | False | N/A | Description for param2
"""
    assert result == expected


def test_docstring_metas_to_md_table_on_self():
    assert docstring_metas_to_md_table.__doc__ is not None
    docstring = parse(docstring_metas_to_md_table.__doc__, style=Style.NUMPYDOC)
    result_params = docstring_metas_to_md_table("Parameters", 2, docstring.params)
    expected_params = """## Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
name | str | False | N/A | Name of the docstring meta (ex: Parameters, Returns, Raises)
level | int | False | N/A | Heading level for the markdown table
meta | list[DocstringMetaT] | False | N/A | List of docstring meta items to include in the table
"""
    assert result_params == expected_params

    assert docstring.returns is not None
    result_returns = docstring_metas_to_md_table("Returns", 2, [docstring.returns])
    expected_returns = """## Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
str | N/A | False | Markdown table representation of the docstring meta items
"""
    assert result_returns == expected_returns


def test_docstring_element_repr():
    assert DocToMarkdownElement.__doc__ is not None
    element = ClassElement(DocToMarkdownElement, include_private=True)
    expected_repr = """## DocToMarkdownElement
```Python
class DocToMarkdownElement(DocToMarkdownElementProtocol)
```
Base class for elements that can be included in the markdown documentation (ex: functions, classes, methods)

### Attributes
Attribute | Type | Optional | Default | Description
--- | --- | --- | --- | ---
name | str | False | N/A | Name of the element (ex: function name, class name)
docstring | Docstring | False | N/A | Parsed docstring object for the element
signature | str | False | N/A | Signature of the element (ex: function signature)
level | int | False | N/A | Heading level for the element in the markdown documentation (ex: 1 for module, 2 for class, 3 for method)
### Methods
Method | Description
--- | ---
[__init__](#__init__) | Initialize the element with its name, docstring, signature, and heading level.
[__repr__](#__repr__) | String representation of the element in markdown format.

### __init__
```Python
def __init__(self, name: str, docstring: docstring_parser.common.Docstring, level: int, signature: str | None = None)
```
Initialize the element with its name, docstring, signature, and heading level.

#### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
name | str | False | N/A | Name of the element (ex: function name, class name)
signature | str | True | None | Signature of the element (ex: function signature)
docstring | Docstring | False | N/A | Parsed docstring object for the element
level | int | False | N/A | Heading level for the element in the markdown documentation (ex: 1 for module, 2 for class, 3 for method)

### __repr__
```Python
def __repr__(self) -> str
```
String representation of the element in markdown format.

#### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
str | N/A | False | Markdown representation of the element.
"""
    assert element.__repr__() == expected_repr
