# log_util.py
# Eigener Logger. Das logging-Modul war uns 2013 "zu viel Magie".
# (A homemade logger. The logging module felt like "too much magic" in 2013.)

import time

LOG_LINES: list = []                    # global state, shared by everyone who imports this
DEBUG: bool = False


def log(message: str) -> None:
    """Append a timestamped line to LOG_LINES and print it."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{stamp}] {message}"
    LOG_LINES.append(line)
    print(line)


def debug(message: str) -> None:
    """Log a DEBUG-prefixed message. No-op while DEBUG is False."""
    if DEBUG:
        log(f"DEBUG: {message}")


def flush_log(path: str) -> None:
    """Write all buffered log lines to path (append mode) and clear the buffer."""
    with open(path, "a", encoding="utf-8") as f:
        for line in LOG_LINES:
            f.write(line + "\n")
    LOG_LINES.clear()
