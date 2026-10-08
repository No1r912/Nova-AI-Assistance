from copy import deepcopy

from core.utils import load_json, save_json
from core.config import SETTINGS_FILE

DEFAULT_SETTINGS = {
    "ai": {"model": "gemma3:4b", "temperature": 0.55},
    "audio": {"input_device": None, "sample_rate": 16000, "record_seconds": 8},
}
settings = load_json(SETTINGS_FILE, {})


def _lookup(mapping, key, default=None):
    current = mapping
    for part in key.split("."):
        if not isinstance(current, dict) or part not in current:
            return default
        current = current[part]
    return current


def get(key, default=None):
    """Return a setting using dotted keys, with a safe project default."""
    value = _lookup(settings, key, None)
    if value is not None:
        return value
    return deepcopy(_lookup(DEFAULT_SETTINGS, key, default))


def set(key, value):
    """Persist a setting using a dotted key (for example, ``ai.model``)."""
    target = settings
    parts = key.split(".")
    for part in parts[:-1]:
        target = target.setdefault(part, {})
    target[parts[-1]] = value

    save_json(
        SETTINGS_FILE,
        settings
    )
