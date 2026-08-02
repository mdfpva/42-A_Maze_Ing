#!/usr/bin/env python3

"""A-Maze-ing: maze generator entry point."""
import sys
from mazegen import parse_config, MazeGenerator, debug_render


def main() -> int:
    """Generate and display a maze."""
    config = parse_config(sys.argv[1] if len(sys.argv) > 1 else "config.txt")

    generator = MazeGenerator(
        width=config.width,
        height=config.height,
        seed=config.seed,
    )

    maze = generator.generate()

    debug_render(maze)

    return 0


if __name__ == "__main__":
    sys.exit(main())
