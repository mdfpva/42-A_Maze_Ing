#!/usr/bin/env python3

from dataclasses import dataclass
from typing import IO
from sys import argv


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message: str = "Cofiguration Error") -> None:
        super().__init__(message)


@dataclass
class Config:
    width:          int
    height:         int
    entry_position: tuple[int, int]
    exit_position:  tuple[int, int]
    output_file:    str
    perfect:        bool


def parse_config(path: str) -> Config:
    try:
        with open(path, "r") as config_fd:
            config_text: str = config_fd.read()
            config_data: list[str] = config_text.split('\n')
            config: dict
            for line in config_data:
                if not line or line.startswith('#'):
                    continue
                if '#' in line:
                    line = line.split('#')[0]
                line = line.strip()
                key, value = line.split('=')
                print(f"key: {key} | value: {value}")
    except (FileNotFoundError, PermissionError) as e:
        print(f"{e}")


if __name__ == "__main__":
    parse_config(argv[1])
