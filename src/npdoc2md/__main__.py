import argparse
import logging
from pathlib import Path

from ._log import logger
from ._version import __version__
from .npdoc2md import npdoc2md
from .utils import create_output_directory, validate_paths


def main():
    """Main entry point for the npdoc2md CLI utility."""

    parser = argparse.ArgumentParser(
        description="Utility for autogenerating markdown from numpy-style docstrings."
    )
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose logging"
    )
    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Enable quiet mode (only errors will be logged)",
    )
    parser.add_argument(
        "--include-private",
        action="store_true",
        help="Include private members (those starting with an underscore)",
    )
    parser.add_argument(
        "--private-whitelist",
        type=str,
        nargs="+",
        default=["__init__", "__repr__"],
        help="List of private member names to include even without --include-private.",
    )
    parser.add_argument(
        "input_path",
        type=str,
        help="Path to the input file or directory containing files to parse",
    )
    parser.add_argument(
        "output_path",
        type=str,
        help="Path to the output directory where markdown files will be saved",
    )
    args = parser.parse_args()

    input_path = Path(args.input_path)
    output_path = Path(args.output_path)

    if not output_path.exists():
        logger.info(
            f"Output path '{output_path}' does not exist. Attempting to create it."
        )
        create_output_directory(output_path)

    validate_paths(input_path, output_path)

    if args.verbose:
        if args.quiet:
            logger.warning(
                "Both --verbose and --quiet flags are set. Defaulting to verbose mode."
            )
        logger.setLevel(logging.DEBUG)
    elif args.quiet:
        logger.setLevel(logging.ERROR)
    else:
        logger.setLevel(logging.INFO)

    for output_file, text in npdoc2md(
        input_path, output_path, ignore_private=args.ignore_private
    ).items():
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
