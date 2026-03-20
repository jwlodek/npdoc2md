import pytest

from npdoc2md import utils as npdoc2md_utils
from npdoc2md.utils import (
    create_output_directory,
    get_cls_and_func_defined_in_module,
    get_target_output_file_path,
    validate_paths,
)


def test_create_output_directory(tmp_path):
    output_dir = tmp_path / "output"
    # Test that the directory is created if it does not exist
    assert not output_dir.exists()
    create_output_directory(output_dir)
    assert output_dir.exists() and output_dir.is_dir()

    # Test that no error is raised if the directory already exists
    create_output_directory(output_dir)
    assert output_dir.exists() and output_dir.is_dir()

    # Test that an error is raised if the directory cannot be created (e.g., due to permissions)
    non_creatable_dir = tmp_path / "non_creatable"
    non_creatable_dir.mkdir()
    non_creatable_dir.chmod(0o400)  # Remove write permissions
    with pytest.raises(PermissionError):
        create_output_directory(non_creatable_dir / "subdir")


def test_validate_paths(tmp_path):
    # Test with valid input and output paths
    input_path = tmp_path / "input"
    output_path = tmp_path / "output"
    input_path.mkdir()
    output_path.mkdir()
    validate_paths(input_path, output_path)

    # Test with non-existent input path
    with pytest.raises(FileNotFoundError):
        validate_paths(tmp_path / "non_existent_input", output_path)

    # Test with non-readable input path
    non_readable_input = tmp_path / "non_readable_input"
    non_readable_input.mkdir()
    non_readable_input.chmod(0o000)  # Remove read permissions
    with pytest.raises(PermissionError):
        validate_paths(non_readable_input, output_path)

    non_readable_input.chmod(0o700)  # Restore permissions for cleanup

    # Test with output path that is a file
    output_file = tmp_path / "output_file"
    output_file.touch()
    with pytest.raises(NotADirectoryError):
        validate_paths(input_path, output_file)

    # Test with non-writable output path
    non_writable_output = tmp_path / "non_writable_output"
    non_writable_output.mkdir()
    non_writable_output.chmod(0o400)  # Remove write permissions
    with pytest.raises(PermissionError):
        validate_paths(input_path, non_writable_output)

    non_writable_output.chmod(0o700)  # Restore permissions for cleanup

    # Test case where input file does not have .py extension
    input_file_without_py_extension = tmp_path / "input_file"
    input_file_without_py_extension.touch()
    with pytest.raises(ValueError):
        validate_paths(input_file_without_py_extension, output_path)


def test_get_target_output_file_path(tmp_path):
    input_base_path = tmp_path / "input"
    output_base_path = tmp_path / "output"
    input_base_path.mkdir()
    output_base_path.mkdir()

    # Test with a simple file
    input_file = input_base_path / "module.py"
    input_file.touch()
    expected_output_file = output_base_path / "module.md"
    output_file = get_target_output_file_path(
        input_file, input_base_path, output_base_path
    )
    assert output_file == expected_output_file

    # Test with a file in a subdirectory
    subdir = input_base_path / "subdir"
    subdir.mkdir()
    input_file_subdir = subdir / "module.py"
    input_file_subdir.touch()
    expected_output_file_subdir = output_base_path / "subdir" / "module.md"
    output_file_subdir = get_target_output_file_path(
        input_file_subdir, input_base_path, output_base_path
    )
    assert output_file_subdir == expected_output_file_subdir


def test_get_cls_func_defined_in_module():
    classes, functions = get_cls_and_func_defined_in_module(npdoc2md_utils)
    assert "validate_paths" in functions
    assert "get_target_output_file_path" in functions
    assert "get_cls_and_func_defined_in_module" in functions
    assert len(classes) == 0  # No classes defined in utils.py
    assert (
        "getLogger" not in functions
    )  # getLogger is imported from logging, not defined in utils.py
