"""Writing the maze to the output file in the subject's format."""

from .maze import Maze


class OutputError(Exception):
    """Raised when the output file cannot be written."""


def maze_lines(maze: Maze, entry: tuple[int, int], exit_: tuple[int, int],
               path: str) -> list[str]:
    """Return the output file lines (without newline characters)."""
    lines = [
        "".join(f"{cell:x}" for cell in row) for row in maze.grid
    ]
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_[0]},{exit_[1]}")
    lines.append(path)
    return lines


def write_maze(path: str, maze: Maze, entry: tuple[int, int],
               exit_: tuple[int, int], solution: str) -> None:
    """Write the maze file; raise OutputError on any OS failure."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            for line in maze_lines(maze, entry, exit_, solution):
                handle.write(line + "\n")
    except OSError as exc:
        raise OutputError(f"Cannot write '{path}': {exc}") from exc
