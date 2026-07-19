#!/usr/bin/env python3
"""Configuration parser and validator for the maze generator."""

from dataclasses import dataclass

MIN_WIDTH = 9
MIN_HEIGHT = 6


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message: str = "Configuration Error") -> None:
        """Initialize the exception with a message."""
        super().__init__(message)


class Validate:
    """Static methods to validate and convert configuration fields."""

    @staticmethod
    def int_field(value_str: str, min_value: int, field_name: str) -> int:
        """Validate if a string is a valid integer above the minimum value."""
        try:
            number = int(value_str)
        except ValueError as e:
            raise ConfigError(f"'{field_name}' must be an integer!") from e

        if number <= min_value:
            msg = f"'{field_name}' must be at least {min_value + 1}!"
            raise ConfigError(msg)
        return number

    @staticmethod
    def coordinate_field(
        value: str, max_x: int, max_y: int, field_name: str
    ) -> tuple[int, int]:
        """Validate if a string is a valid coordinate within maze boundaries."""
        parts: list[str] = value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"Wrong amount of values in '{field_name}'!")

        try:
            x = int(parts[0])
            y = int(parts[1])
        except ValueError as e:
            msg = f"'{field_name}' must be in the following format: x,y"
            raise ConfigError(msg) from e

        if x < 0 or y < 0:
            raise ConfigError(f"'{field_name}' must not be negative!")
        if x >= max_x or y >= max_y:
            msg = (
                f"'{field_name}' position ({x},{y}) is out of "
                f"the maze boundaries ({max_x}x{max_y})!"
            )
            raise ConfigError(msg)
        return (x, y)

    @staticmethod
    def bool_field(value: str, field_name: str) -> bool:
        """Validate and convert a string into a boolean value."""
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ConfigError(f"'{field_name}': value must be boolean!")


@dataclass
class Config:
    """Data class representing a valid maze configuration."""

    width: int
    height: int
    entry_position: tuple[int, int]
    exit_position: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_config(path: str) -> Config:
    """Parse a configuration file and return a valid Config object."""
    config_dict: dict[str, str] = {}
    try:
        with open(path, "r") as config_fd:
            config_text: str = config_fd.read()
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e

    config_data: list[str] = config_text.split("\n")
    for line in config_data:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#")[0].strip()
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        config_dict[key.strip()] = value.strip()

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in config_dict]
    if missing:
        raise ConfigError(f"Missing required keys: {', '.join(missing)}")

    width = Validate.int_field(config_dict["WIDTH"], MIN_WIDTH, "WIDTH")
    height = Validate.int_field(config_dict["HEIGHT"], MIN_HEIGHT, "HEIGHT")
    entry = Validate.coordinate_field(
        config_dict["ENTRY"], width, height, "ENTRY"
    )
    exit_pos = Validate.coordinate_field(
        config_dict["EXIT"], width, height, "EXIT"
    )

    if entry == exit_pos:
        raise ConfigError("ENTRY and EXIT positions must be different!")

    perfect = Validate.bool_field(config_dict["PERFECT"], "PERFECT")
    output_file = config_dict["OUTPUT_FILE"]

    seed: int | None = None
    if "SEED" in config_dict:
        try:
            seed = int(config_dict["SEED"])
        except ValueError as e:
            raise ConfigError("'SEED' must be an integer!") from e

    return Config(width, height, entry, exit_pos, output_file, perfect, seed)
