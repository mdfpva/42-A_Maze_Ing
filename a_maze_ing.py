#!/usr/bin/env python3
"""A-Maze-ing: maze generator entry point."""

import sys

from mazegen import (
    ConfigError,
    MazeGenerator,
    render,
    parse_config,
    shortest_path,
    write_maze,
    OutputError,
    pattern_cells,
    Config
)


CLEAR = "\033[2J\033[H"


def interact(config: Config) -> None:
    """Run the interactive display loop."""
    blocked = pattern_cells(config.width, config.height)
    show_path = False
    color = 0
    maze = MazeGenerator(config.width, config.height, config.seed,
                         config.perfect, blocked).generate()
    solution = shortest_path(maze, config.entry_position,
                             config.exit_position)

    while True:
        print(CLEAR, end="")
        path = solution if show_path else None
        render(maze, config.entry_position, config.exit_position,
               path, color)
        print("\n1. Regenerate  2. Show/Hide path  "
              "3. Change color  4. Quit")
        try:
            choice = input("Choice? ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if choice == "1":
            maze = MazeGenerator(config.width, config.height, None,
                                 config.perfect, blocked).generate()
            solution = shortest_path(maze, config.entry_position,
                                     config.exit_position)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color += 1
        elif choice == "4":
            break
        else:
            print("Invalid choice.")


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

    blocked = pattern_cells(
        config.width,
        config.height
    )
    if not blocked:
        print("Note: maze too small for the '42' pattern; omitted.")
    if config.entry_position in blocked:
        print(f"Error: ENTRY {config.entry_position} is inside the "
              f"'42' pattern", file=sys.stderr)
        return 1
    if config.exit_position in blocked:
        print(f"Error: EXIT {config.exit_position} is inside the "
              f"'42' pattern", file=sys.stderr)
        return 1

    maze = MazeGenerator(
        config.width,
        config.height,
        config.seed,
        config.perfect,
        blocked
    ).generate()

    solution = shortest_path(
        maze,
        config.entry_position,
        config.exit_position
    )
    if solution is None:
        print("Error: no path between entry and exit", file=sys.stderr)
        return 1

    try:
        write_maze(
            config.output_file,
            maze,
            config.entry_position,
            config.exit_position,
            solution
        )
    except OutputError as error:
        print(f"Output error: {error}", file=sys.stderr)
        return 1

    interact(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
