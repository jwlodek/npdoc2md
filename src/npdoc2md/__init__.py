"""Package for converting Python docstrings to Markdown documentation."""

__copyright__ = "2026"
__author__ = "Jakub Wlodek"
__url__ = "https://github.com/jwlodek/npdoc2md"

from ._version import __version__
from .npdoc2md import npdoc2md

__all__ = ["__version__", "npdoc2md"]
