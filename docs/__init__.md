# npdoc2md.npdoc2md
Module for converting docstrings in Python files to markdown format.

This module defines the main functionality for the npdoc2md package, which includes:
- Classes for representing docstring elements (ModuleElement, ClassElement, FunctionDocstring)
- A helper function for converting docstring meta information to markdown tables
- The main function npdoc2md that orchestrates the process of converting docstrings to markdown
## Classes
Classe | Description
--- | ---
[ClassElement](#ClassElement) | Class for representing class docstrings, which can contain methods as sub-elements.
[DocToMarkdownElement](#DocToMarkdownElement) | Base class for elements that can be included in the markdown documentation (ex: functions, classes, methods)
[DocToMarkdownElementProtocol](#DocToMarkdownElementProtocol) | Description for DocToMarkdownElementProtocol
[FunctionElement](#FunctionElement) | Class for representing function docstrings.
[ModuleElement](#ModuleElement) | Class for representing module docstrings, which can contain classes and functions as sub-elements.
## Functions
Function | Description
--- | ---
[docstring_metas_to_md_table](#docstring_metas_to_md_table) | Helper function to convert docstring meta to markdown table
[get_target_python_files](#get_target_python_files) | Helper function to get list of target python files to process
[npdoc2md](#npdoc2md) | Main function for converting docstrings to markdown

## ClassElement
```Python
class ClassElement(DocToMarkdownElement)
```
Class for representing class docstrings, which can contain methods as sub-elements.

### Attributes
Attribute | Type | Optional | Default | Description
--- | --- | --- | --- | ---
methods | list[FunctionElement] | False | N/A | List of methods defined in the class, represented as FunctionElement objects
### Methods
Method | Description
--- | ---
[__init__](#__init__) | Initalize Class Docstring representation with the class's name, signature, docstring, and heading level.

### __init__
```Python
def __init__(self, cls: type, include_private: bool = False)
```
Initalize Class Docstring representation with the class's name, signature, docstring, and heading level.

#### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
cls | type | False | N/A | The class to parse for docstrings and sub-elements
include_private | Optional[bool]; default False | False | N/A | Whether to include private members (those starting with an underscore) in the documentation.

## DocToMarkdownElement
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
signature | str | None, optional, default=None | False | N/A | Signature of the element (ex: function signature)
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

## DocToMarkdownElementProtocol
```Python
class DocToMarkdownElementProtocol(Protocol)
```
Description for DocToMarkdownElementProtocol
### Methods
Method | Description
--- | ---
[__init__](#__init__) | Description for __init__()

### __init__
```Python
def __init__(self, *args, **kwargs)
```
Description for __init__()

## FunctionElement
```Python
class FunctionElement(DocToMarkdownElement)
```
Class for representing function docstrings.

## ModuleElement
```Python
class ModuleElement(DocToMarkdownElement)
```
Class for representing module docstrings, which can contain classes and functions as sub-elements.

### Attributes
Attribute | Type | Optional | Default | Description
--- | --- | --- | --- | ---
classes | list[ClassElement] | False | N/A | List of classes defined in the module, represented as ClassElement objects
functions | list[FunctionDocstring] | False | N/A | List of functions defined in the module, represented as FunctionDocstring objects
### Methods
Method | Description
--- | ---
[__init__](#__init__) | Initialize the ModuleElement with the module's name, signature, docstring, and heading level.

### __init__
```Python
def __init__(self, module: module, include_private: bool = False)
```
Initialize the ModuleElement with the module's name, signature, docstring, and heading level.

Also parses the classes and functions defined in the module as sub-elements.
#### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
module | ModuleType | False | N/A | The module to parse for docstrings and sub-elements
include_private | Optional[bool]; default False | False | N/A | Whether to include private members (those starting with an underscore) in the documentation.

## docstring_metas_to_md_table
```Python
def docstring_metas_to_md_table(name: str, level: int, meta: list[~TableItemT]) -> str
```
Helper function to convert docstring meta to markdown table

### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
name | str | False | N/A | Name of the docstring meta (ex: Parameters, Returns, Raises)
level | int | False | N/A | Heading level for the markdown table
meta | list[DocstringMetaT] | False | N/A | List of docstring meta items to include in the table
### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
str | N/A | False | Markdown table representation of the docstring meta items

## get_target_python_files
```Python
def get_target_python_files(input_path: pathlib._local.Path, ignore_private: bool) -> List[pathlib._local.Path]
```
Helper function to get list of target python files to process

### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
input_path | Path | False | N/A | Path to the input file or directory containing files to parse
ignore_private | bool | False | N/A | Whether to ignore private members (those starting with an underscore)
### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
List[Path] | N/A | False | List of paths to target python files to process

## npdoc2md
```Python
def npdoc2md(input_path: pathlib._local.Path, output_path: pathlib._local.Path, ignore_private: bool = False) -> dict[pathlib._local.Path, str]
```
Main function for converting docstrings to markdown

This function orchestrates the process of converting docstrings in Python files to markdown format.
It identifies the target Python files, imports them to access their docstrings,
and then parses the docstrings to generate markdown documentation.
### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
input_path | Path | False | N/A | Path to the input file or directory containing files to parse
output_path | Path | False | N/A | Path to the output directory where markdown files will be saved
ignore_private | bool | True | False | Whether to ignore private members (those starting with an underscore), by default False
