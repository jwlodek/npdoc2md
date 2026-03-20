import logging
import subprocess
import sys
from io import StringIO
from pathlib import Path

import pytest
from npdoc2md._version import __version__
from pytest import LogCaptureFixture, MonkeyPatch

from npdoc2md.__main__ import main
from npdoc2md._log import COLOR_MAP, ColorFormatter, handler, logger


def test_version():
    result = subprocess.run(["npdoc2md", "--version"], capture_output=True, text=True)
    assert result.returncode == 0
    assert result.stdout.strip() == __version__


@pytest.mark.parametrize("as_subprocess", [True, False])
def test_generate_md_from_npdoc2md_utils(
    tmp_path: Path, as_subprocess: bool, monkeypatch: MonkeyPatch
):
    output_dir = tmp_path if as_subprocess else tmp_path / "nonexistant_dir"

    if as_subprocess:
        result = subprocess.run(
            ["npdoc2md", "src/npdoc2md/utils.py", str(output_dir)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
    else:
        monkeypatch.setattr(
            sys, "argv", ["npdoc2md", "src/npdoc2md/utils.py", str(output_dir)]
        )
        main()

    generated_file = output_dir / "utils.md"
    assert generated_file.exists() and generated_file.is_file()

    with open(generated_file) as fp:
        generated_md = fp.read()

    with open("tests/expected_output/utils.md") as fp:
        expected_md = fp.read()

    assert generated_md == expected_md


def test_quiet_and_verbose_results_in_verbose_logging(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture, tmp_path: Path
):
    # Test that --quiet overrides --verbose
    monkeypatch.setattr(
        sys,
        "argv",
        ["npdoc2md", "--verbose", "--quiet", "src/npdoc2md/utils.py", str(tmp_path)],
    )

    with caplog.at_level("DEBUG"):
        main()

    assert (
        "Both --verbose and --quiet flags are set. Defaulting to verbose mode."
        in caplog.text
    )
    assert logging.getLogger("npdoc2md").getEffectiveLevel() == logging.DEBUG


def test_quiet_results_in_only_error_logging(
    monkeypatch: MonkeyPatch, caplog: LogCaptureFixture, tmp_path: Path
):
    # Test that --quiet results in only error logging
    monkeypatch.setattr(
        sys, "argv", ["npdoc2md", "--quiet", "src/npdoc2md/utils.py", str(tmp_path)]
    )

    with caplog.at_level("ERROR"):
        main()

    assert logging.getLogger("npdoc2md").getEffectiveLevel() == logging.ERROR


def test_log_levels_in_color(monkeypatch: MonkeyPatch, tmp_path: Path):
    # Test that log levels are color coded in the output.
    # caplog uses its own formatter (no ANSI codes), so we need to capture
    # the output of our custom ColorFormatter handler directly.
    monkeypatch.setattr(
        sys,
        "argv",
        ["npdoc2md", "--verbose", "--quiet", "src/npdoc2md/utils.py", str(tmp_path)],
    )

    # Reset the logger level to INFO before running main(), since previous
    # tests may have changed it (e.g. to ERROR via --quiet). The WARNING
    # message in main() is emitted *before* --verbose sets the level to DEBUG,
    # so it would be suppressed if the level were still ERROR from a prior test.
    logger.setLevel(logging.INFO)

    # Replace the handler's stream with a StringIO to capture output,
    # and set use_color=True on the formatter (since isatty() is evaluated
    # at import time and will be False in a test environment).
    captured = StringIO()
    monkeypatch.setattr(handler, "stream", captured)
    fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    monkeypatch.setattr(handler, "formatter", ColorFormatter(fmt, use_color=True))

    main()

    output = captured.getvalue()

    # Check that the log levels in the captured output contain ANSI color codes
    assert f"{COLOR_MAP[logging.DEBUG]}DEBUG" in output  # DEBUG should be cyan
    assert f"{COLOR_MAP[logging.INFO]}INFO" in output  # INFO should be green
    assert (
        f"{COLOR_MAP[logging.WARNING]}WARNING" in output
    )  # WARNING should be bright yellow
