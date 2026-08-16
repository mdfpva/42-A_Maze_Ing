#!/usr/bin/env python3
"""ASCII rendering utilities."""

from .maze import Maze, NORTH, EAST, WEST


RESET = "\033[0m"


PATH_COLOR = "\033[92m"


PALETTE = ("\033[37m", "\033[33m", "\033[36m", "\033[35m", "\033[32m")


def path_cells(
        entry: tuple[int, int],
        path: str
        ) -> set[tuple[int, int]]:
    """Return the set of cells crossed by a letter path from entry."""
    steps = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry
    cells = {entry}
    for letter in path:
        dx, dy = steps[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def render(
        maze: Maze,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: str | None = None,
        color: int = 0
        ) -> None:
    """Print a rough ASCII view of the maze."""
    wall_color = PALETTE[color % len(PALETTE)]
    marked = path_cells(entry, path) if path else set()
    for y in range(maze.height):
        top = ""
        mid = ""
        for x in range(maze.width):
            top += "+--" if maze.has_wall(x, y, NORTH) else "+  "
            if (x, y) in marked:
                inside = PATH_COLOR + "()" + wall_color
            else:
                inside = "  "
            mid += ("|" if maze.has_wall(x, y, WEST) else " ") + inside
        print(wall_color + top + "+" + RESET)
        east = "|" if maze.has_wall(maze.width - 1, y, EAST) else " "
        print(wall_color + mid + east + RESET)
    print(wall_color + "+--" * maze.width + "+" + RESET)
