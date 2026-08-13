#!/usr/bin/env python3
"""Tests for the maze solver."""

from mazegen import MazeGenerator, shortest_path, Maze
from mazegen import NORTH, EAST, SOUTH, WEST

def follow_path(maze: Maze, start: tuple[int, int], path: str) -> tuple[int, int]:
    """Walk a letter path from start, asserting every step is open."""
    steps = {"N": (0, -1, NORTH), "E": (1, 0, EAST),
             "S": (0, 1, SOUTH), "W": (-1, 0, WEST)}
    x, y = start
    for letter in path:
        dx, dy, direction = steps[letter]
        assert not maze.has_wall(x, y, direction)
        x, y = x + dx, y + dy
    return (x, y)


def test_solver_returns_valid_shortest_path() -> None:
    """The solver's path is walkable and reaches the goal."""
    maze = MazeGenerator(10, 10, seed=1, perfect=False).generate()
    path = shortest_path(maze, (0, 0), (9, 9))
    assert path is not None
    assert follow_path(maze, (0, 0), path) == (9, 9)
