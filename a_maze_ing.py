#!/usr/bin/env python3

"""A-Maze-ing: maze generator entry point."""
import sys
from mazegen.config import ConfigError, parse_config


def main() -> int:
    """Run the maze generator program."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1

    try:
        config = parse_config(sys.argv[1])
    except ConfigError as e:
        print(e, file=sys.stderr)
        return 1

    print(config)
    return 0


if __name__ == "__main__":
    sys.exit(main())
