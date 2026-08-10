"""Terminal ASCII rendering with ANSI colours."""

from .maze import EAST, NORTH, WEST, Maze

RESET = "\033[0m"
COLOURS = ("\033[37m", "\033[33m", "\033[36m", "\033[35m")  # w, y, c, m
PATH_COLOUR = "\033[32m"
ENTRY_COLOUR = "\033[95m"
EXIT_COLOUR = "\033[91m"
BLOCK_COLOUR = "\033[90m"


def path_cells(entry: tuple[int, int], path: str) -> set[tuple[int, int]]:
    """Return every cell crossed by a letter path starting at entry."""
    steps = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry
    cells = {entry}
    for letter in path:
        dx, dy = steps[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def render(maze: Maze, entry: tuple[int, int], exit_: tuple[int, int],
           path: str | None = None, colour: int = 0) -> str:
    """Return the maze as a coloured ASCII string."""
    wall = COLOURS[colour % len(COLOURS)]
    marks = path_cells(entry, path) if path else set()
    out: list[str] = []
    for y in range(maze.height):
        top: list[str] = []
        mid: list[str] = []
        for x in range(maze.width):
            top.append("+--" if maze.has_wall(x, y, NORTH) else "+  ")
            side = "|" if maze.has_wall(x, y, WEST) else " "
            interior = _cell(maze, x, y, entry, exit_, marks)
            mid.append(wall + side + RESET + interior)
        out.append(wall + "".join(top) + "+" + RESET)
        east = "|" if maze.has_wall(maze.width - 1, y, EAST) else " "
        out.append("".join(mid) + wall + east + RESET)
    out.append(wall + "+--" * maze.width + "+" + RESET)
    return "\n".join(out)


def _cell(maze: Maze, x: int, y: int, entry: tuple[int, int],
          exit_: tuple[int, int], marks: set[tuple[int, int]]) -> str:
    """Return the 2-character interior of one cell."""
    if (x, y) == entry:
        return ENTRY_COLOUR + "In" + RESET
    if (x, y) == exit_:
        return EXIT_COLOUR + "Ex" + RESET
    if (x, y) in maze.blocked:
        return BLOCK_COLOUR + "##" + RESET
    if (x, y) in marks:
        return PATH_COLOUR + "()" + RESET
    return "  "
