# npdoc2md.utils
Description for npdoc2md.utils module
## Functions
Function | Description
--- | ---
[create_output_directory](#create_output_directory) | Create the output directory if it does not exist.
[get_cls_and_func_defined_in_module](#get_cls_and_func_defined_in_module) | Get the sets of class and function names defined in a module.
[get_target_output_file_path](#get_target_output_file_path) | Get the output file path for a given input file, preserving directory structure.
[sanitize_signature](#sanitize_signature) | Sanitize a signature by replacing invalid types with their correct names.
[validate_paths](#validate_paths) | Validate the input and output paths.

## create_output_directory
```Python
def create_output_directory(output_path: pathlib.Path) -> None
```
Create the output directory if it does not exist.

### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
output_path | Path | False | N/A | The path to the output directory.
### Raises
Error | Description
--- | ---
PermissionError | If the output directory cannot be created due to permission issues.

## get_cls_and_func_defined_in_module
```Python
def get_cls_and_func_defined_in_module(module: module) -> tuple[dict[str, type], dict[str, collections.abc.Callable]]
```
Get the sets of class and function names defined in a module.

### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
module | ModuleType | False | N/A | The module to inspect.
### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
tuple[dict[str, type], dict[str, Callable]] | N/A | False | A tuple containing two dictionaries: the first maps class names to class objects, and the second maps function names to function objects, for all classes and functions defined in the given module.

## get_target_output_file_path
```Python
def get_target_output_file_path(input_file: pathlib.Path, input_base_path: pathlib.Path, output_base_path: pathlib.Path) -> pathlib.Path
```
Get the output file path for a given input file, preserving directory structure.

### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
input_file | Path | False | N/A | The path to the input Python file.
input_base_path | Path | False | N/A | The base path of the input files (used to determine relative paths).
output_base_path | Path | False | N/A | The base path for the output markdown files.
### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
Path | N/A | False | The path to the output markdown file.

## sanitize_signature
```Python
def sanitize_signature(signature: str) -> str
```
Sanitize a signature by replacing invalid types with their correct names.

This is necessary because some types are represented in the signature
as their internal names (e.g., '_io.BytesIO' instead of 'io.BytesIO'),
which can be confusing. This function uses a predefined mapping to replace these
invalid type representations with their correct, fully qualified names.
### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
signature | str | False | N/A | The original function or method signature to sanitize.
### Returns
Type | Variable Name | Is Generator | Description
--- | --- | --- | ---
str | N/A | False | The sanitized signature with invalid types replaced by their correct names.

## validate_paths
```Python
def validate_paths(input_path: pathlib.Path, output_path: pathlib.Path) -> None
```
Validate the input and output paths.

Checks if the input path exists and is readable, and if the output path
is a directory that can be created or is writable.
### Raises
Error | Description
--- | ---
FileNotFoundError | If the input path does not exist.
PermissionError | If the input/output paths are not readable/writable.
NotADirectoryError | If the output path exists but is a file instead of a directory.
