#!/usr/bin/env python3

"""A-Maze-ing: maze generator entry point."""

import sys

from mazegen import (
    ConfigError,
    MazeGenerator,
    render,
    parse_config,
)


def main() -> int:
    """Generate and display a maze."""
    if len(sys.argv) != 2:
        print(
            "Usage: python3 a_maze_ing.py config.txt",
            file=sys.stderr,
        )
        return 1

    try:
        config = parse_config(sys.argv[1])
    except ConfigError as error:
        print(f"Config error: {error}", file=sys.stderr)
        return 1

    maze = MazeGenerator(
        config.width,
        config.height,
        config.seed,
        config.perfect
    ).generate()

    render(maze)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
