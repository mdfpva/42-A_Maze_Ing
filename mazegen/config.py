"""Configuration file parsing and validation."""

from dataclasses import dataclass


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""


@dataclass(frozen=True)
class Config:
    """A validated maze configuration."""

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


REQUIRED = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT")


def _to_int(value: str, key: str) -> int:
    """Convert ``value`` to int or raise a clear ConfigError."""
    try:
        return int(value)
    except ValueError as exc:
        raise ConfigError(f"{key} must be an integer, got '{value}'") from exc


def _to_size(value: str, key: str) -> int:
    """Convert ``value`` to a positive dimension."""
    number = _to_int(value, key)
    if number < 1:
        raise ConfigError(f"{key} must be at least 1, got {number}")
    return number


def _to_coords(value: str, key: str, width: int,
               height: int) -> tuple[int, int]:
    """Convert 'x,y' to coordinates inside the maze bounds."""
    parts = value.split(",")
    if len(parts) != 2:
        raise ConfigError(f"{key} must use the format x,y, got '{value}'")
    x, y = _to_int(parts[0], key), _to_int(parts[1], key)
    if not (0 <= x < width and 0 <= y < height):
        raise ConfigError(
            f"{key} ({x},{y}) is outside the {width}x{height} maze")
    return x, y


def _to_bool(value: str, key: str) -> bool:
    """Convert a True/False string to bool."""
    lowered = value.lower()
    if lowered in ("true", "1", "yes"):
        return True
    if lowered in ("false", "0", "no"):
        return False
    raise ConfigError(f"{key} must be True or False, got '{value}'")


def _read_pairs(path: str) -> dict[str, str]:
    """Read KEY=VALUE pairs from ``path``, ignoring comments."""
    pairs: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as handle:
            for raw in handle:
                line = raw.split("#", 1)[0].strip()
                if not line:
                    continue
                if "=" not in line:
                    raise ConfigError(
                        f"Invalid line (missing '='): '{raw.strip()}'")
                key, value = line.split("=", 1)
                pairs[key.strip()] = value.strip()
    except OSError as exc:
        raise ConfigError(f"Cannot read '{path}': {exc}") from exc
    return pairs


def parse_config(path: str) -> Config:
    """Parse and validate the configuration file at ``path``."""
    pairs = _read_pairs(path)
    missing = [key for key in REQUIRED if key not in pairs]
    if missing:
        raise ConfigError(f"Missing required keys: {', '.join(missing)}")
    width = _to_size(pairs["WIDTH"], "WIDTH")
    height = _to_size(pairs["HEIGHT"], "HEIGHT")
    entry = _to_coords(pairs["ENTRY"], "ENTRY", width, height)
    exit_ = _to_coords(pairs["EXIT"], "EXIT", width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different")
    if not pairs["OUTPUT_FILE"]:
        raise ConfigError("OUTPUT_FILE must not be empty")
    seed = _to_int(pairs["SEED"], "SEED") if "SEED" in pairs else None
    return Config(width, height, entry, exit_, pairs["OUTPUT_FILE"],
                  _to_bool(pairs["PERFECT"], "PERFECT"), seed)
