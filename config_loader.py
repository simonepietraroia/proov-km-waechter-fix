# config_loader.py
# Liest settings.cfg. Selbst geschrieben, weil uns ConfigParser 2013 "zu kompliziert" war.
# (Reads settings.cfg. Hand-rolled, because ConfigParser felt "too complicated" in 2013.)

from typing import Optional

SETTINGS_FILE = "settings.cfg"

KNOWN_KEYS = [
    "service_interval_km",
    "warn_at_percent",
    "report_title",
    "history_file",
    "log_file",
    "mileage_unit",
]


def load_settings(path: Optional[str] = None) -> dict:
    """Read settings.cfg (or the given path) and return a dict of known key/value pairs.

    Unknown keys are silently ignored; all values are returned as strings.
    """
    if path is None:
        path = SETTINGS_FILE
    settings = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line == "" or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            # Unknown keys are silently dropped, so a typo never surfaces.
            if key in KNOWN_KEYS:
                settings[key] = value
    return settings


def get_int(settings: dict, key: str, fallback: int) -> int:
    """Return settings[key] as an int, or fallback if the key is absent or not a valid int."""
    if key in settings:
        try:
            return int(settings[key])
        except ValueError:
            return fallback
    return fallback


def get_setting(settings: dict, key: str, fallback: str = "") -> str:
    """Return settings[key], or fallback if the key is absent. (Equivalent to dict.get.)"""
    return settings.get(key, fallback)
