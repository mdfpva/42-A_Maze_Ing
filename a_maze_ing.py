#!/usr/bin/env python3

"""A-Maze-ing: maze generator entry point."""
import sys


def main() -> int:
    """Run the maze generator program."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    print(f"Config file: {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
