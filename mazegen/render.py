#!/usr/bin/env python3
"""ASCII rendering utilities."""

from .maze import Maze, NORTH, EAST, WEST


def render(maze: Maze) -> None:
    """Print a rough ASCII view of the maze."""
    for y in range(maze.height):
        top = ""
        mid = ""
        for x in range(maze.width):
            top += "+--" if maze.has_wall(x, y, NORTH) else "+  "
            mid += "|  " if maze.has_wall(x, y, WEST) else "   "
        print(top + "+")
        print(mid + ("|" if maze.has_wall(maze.width - 1, y, EAST) else " "))
    print("+--" * maze.width + "+")
