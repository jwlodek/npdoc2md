import logging
import sys

logging.basicConfig()

logger = logging.getLogger("npdoc2md")

# ANSI color codes for different log levels
COLOR_MAP = {
    logging.DEBUG: "\033[36m",  # Cyan
    logging.INFO: "\033[32m",  # Green
    logging.WARNING: "\033[33;1m",  # Bright Yellow
    logging.ERROR: "\033[31;1m",  # Bright Red
    logging.CRITICAL: "\033[41;97m",  # White on Red bg
}
# ANSI reset code to clear formatting after the log level
RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    """ANSI color formatter for warnings and errors.

    Attributes
    ----------
    use_color : bool
        Whether to use ANSI color codes in the output.
    """

    def __init__(self, fmt: str, use_color: bool = True):
        """Initialize the ColorFormatter.

        Parameters
        ----------
        fmt : str
            The log message format string.
        use_color : bool, optional
            Whether to use ANSI color codes in the output. Defaults to True.
        """

        super().__init__(fmt)
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record with optional color coding based on the log level."""
        if self.use_color and record.levelno in COLOR_MAP:
            # Temporarily modify the levelname with color codes
            original_levelname = record.levelname
            # Pad to 8 characters (length of "CRITICAL") for consistent alignment
            padded_levelname = original_levelname.ljust(8)
            record.levelname = f"{COLOR_MAP[record.levelno]}{padded_levelname}{RESET}"
            base = super().format(record)
            # Restore the original levelname
            record.levelname = original_levelname
            return base
        # For non-colored output, still pad for consistency
        original_levelname = record.levelname
        record.levelname = original_levelname.ljust(8)
        base = super().format(record)
        record.levelname = original_levelname
        return base


handler = logging.StreamHandler()
use_color = sys.stderr.isatty()
fmt = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
handler.setFormatter(ColorFormatter(fmt, use_color=use_color))
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logger.propagate = False
