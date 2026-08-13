#!/usr/bin/env python3
"""Writing the maze to the output file (subject format)."""

from .maze import Maze


class OutputError(Exception):
    """Raised when the output file cannot be written."""


def write_maze(path: str, maze: Maze, entry: tuple[int, int],
               exit_: tuple[int, int], solution: str) -> None:
    """Write the maze to ``path`` in the subject format."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            for line in maze_lines(maze, entry, exit_, solution):
                handle.write(line + "\n")
    except OSError as exc:
        raise OutputError(f"Cannot write '{path}': {exc}") from exc


def maze_lines(maze: Maze, entry: tuple[int, int],
               exit_: tuple[int, int], path: str) -> list[str]:
    """Return the output file lines, without trailing newlines."""
    lines = [
        "".join(f"{cell:x}" for cell in row)
        for row in maze.grid
    ]
    lines.append("")                       # linha em branco
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_[0]},{exit_[1]}")
    lines.append(path)
    return lines
