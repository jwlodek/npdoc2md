# npdoc2md._log
Description for npdoc2md._log module
## Classes
Classe | Description
--- | ---
[ColorFormatter](#ColorFormatter) | ANSI color formatter for warnings and errors.

## ColorFormatter
```Python
class ColorFormatter(Formatter)
```
ANSI color formatter for warnings and errors.

### Attributes
Attribute | Type | Optional | Default | Description
--- | --- | --- | --- | ---
use_color | bool | False | N/A | Whether to use ANSI color codes in the output.
### Methods
Method | Description
--- | ---
[__init__](#__init__) | Initialize the ColorFormatter.
[format](#format) | Format the log record with optional color coding based on the log level.

### __init__
```Python
def __init__(self, fmt: str, use_color: bool = True)
```
Initialize the ColorFormatter.

#### Parameters
Parameter | Type | Optional | Default | Description
--- | --- | --- | --- | ---
fmt | str | False | N/A | The log message format string.
use_color | bool | True | True | Whether to use ANSI color codes in the output. Defaults to True.

### format
```Python
def format(self, record: logging.LogRecord) -> str
```
Format the log record with optional color coding based on the log level.
