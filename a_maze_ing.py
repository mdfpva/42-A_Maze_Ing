"""A-Maze-ing: generate a maze from a config file and display it."""

import sys, os

from mazegen import (
    Config,
    ConfigError,
    Maze,
    MazeGenerator,
    OutputError,
    fits,
    parse_config,
    pattern_cells,
    render,
    shortest_path,
    write_maze,
)

MENU = (
    "\n=== A-Maze-ing ===\n"
    "1. Re-generate a new maze\n"
    "2. Show / Hide the shortest path\n"
    "3. Rotate the wall colours\n"
    "4. Quit\n"
    "Choice? (1-4): "
)


def build_maze(config: Config, seed: int | None) -> tuple[Maze, str]:
    """Generate one maze and its solution; write the output file."""
    blocked = pattern_cells(config.width, config.height)
    generator = MazeGenerator(config.width, config.height, seed,
                              config.perfect, blocked)
    maze = generator.generate()
    solution = shortest_path(maze, config.entry, config.exit)
    if solution is None:
        raise OutputError("No path between ENTRY and EXIT")
    write_maze(config.output_file, maze, config.entry, config.exit,
               solution)
    return maze, solution


def check_config(config: Config) -> None:
    """Reject entry/exit positions that fall inside the "42" pattern."""
    blocked = pattern_cells(config.width, config.height)
    for name, cell in (("ENTRY", config.entry), ("EXIT", config.exit)):
        if cell in blocked:
            raise ConfigError(
                f"{name} {cell[0]},{cell[1]} is inside the '42' pattern")


def interact(config: Config) -> None:
    """Run the display/interaction loop until the user quits."""
    seed = config.seed
    maze, solution = build_maze(config, seed)
    show_path = False
    colour = 0
    while True:
        os.system("clear")
        print(render(maze, config.entry, config.exit,
                     solution if show_path else None, colour))
        try:
            choice = input(MENU).strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        if choice == "1":
            seed = None if seed is None else seed + 1
            maze, solution = build_maze(config, seed)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            colour += 1
        elif choice == "4":
            return
        else:
            print("Please choose a number between 1 and 4.")


def main() -> int:
    """Program entry point."""
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 1
    try:
        config = parse_config(sys.argv[1])
        check_config(config)
        if not fits(config.width, config.height):
            print("Maze too small for the '42' pattern: omitted.")
        interact(config)
    except (ConfigError, OutputError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
