# npdoc2md.utils
Description for npdoc2md.utils module
## Functions
Function | Description
--- | ---
[get_cls_and_func_defined_in_module](#get_cls_and_func_defined_in_module) | Get the sets of class and function names defined in a module.
[get_target_output_file_path](#get_target_output_file_path) | Get the output file path for a given input file, preserving directory structure.
[validate_paths](#validate_paths) | Validate the input and output paths.

## get_cls_and_func_defined_in_module
```Python
def get_cls_and_func_defined_in_module(module: module) -> tuple[dict[str, type], dict[str, typing.Callable]]
```
Get the sets of class and function names defined in a module.

## get_target_output_file_path
```Python
def get_target_output_file_path(input_file: pathlib._local.Path, input_base_path: pathlib._local.Path, output_base_path: pathlib._local.Path) -> pathlib._local.Path
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

## validate_paths
```Python
def validate_paths(input_path: pathlib._local.Path, output_path: pathlib._local.Path) -> None
```
Validate the input and output paths.

Checks if the input path exists and is readable, and if the output path is a directory that can be created or is writable.
### Raises
Error | Description
--- | ---
FileNotFoundError | If the input path does not exist.
PermissionError | If the input path is not readable or if the output path cannot be created or is not writable.
NotADirectoryError | If the output path exists but is a file instead of a directory.
