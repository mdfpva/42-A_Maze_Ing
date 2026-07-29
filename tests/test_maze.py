#!/usr/bin/env python3
"""Tests for the Maze grid structure."""

import pytest

from mazegen import Maze, MazeError, NORTH, EAST, SOUTH, WEST


def test_new_maze_has_all_walls_closed() -> None:
    """Every cell of a fresh maze must have all 4 walls."""
    maze = Maze(4, 3)
    for y in range(3):
        for x in range(4):
            for direction in (NORTH, EAST, SOUTH, WEST):
                assert maze.has_wall(x, y, direction)


def test_in_bounds() -> None:
    """in_bounds accepts inside cells and rejects outside ones."""
    maze = Maze(5, 5)
    assert maze.in_bounds(0, 0)
    assert maze.in_bounds(4, 4)
    assert not maze.in_bounds(5, 4)
    assert not maze.in_bounds(4, 5)
    assert not maze.in_bounds(-1, 0)
    assert not maze.in_bounds(0, -1)


def test_open_wall_is_symmetric() -> None:
    """Opening a wall opens the matching wall of the neighbor."""
    maze = Maze(5, 5)
    maze.open_wall(1, 1, EAST)
    assert not maze.has_wall(1, 1, EAST)
    assert not maze.has_wall(2, 1, WEST)
    # the other walls are untouched
    assert maze.has_wall(1, 1, NORTH)
    assert maze.has_wall(1, 1, SOUTH)
    assert maze.has_wall(1, 1, WEST)


def test_open_wall_is_idempotent() -> None:
    """Opening the same wall twice must not corrupt the cell."""
    maze = Maze(5, 5)
    maze.open_wall(2, 2, NORTH)
    maze.open_wall(2, 2, NORTH)
    assert not maze.has_wall(2, 2, NORTH)
    assert maze.has_wall(2, 2, EAST)
    assert maze.has_wall(2, 2, SOUTH)
    assert maze.has_wall(2, 2, WEST)


def test_cannot_open_outer_border() -> None:
    """The external border walls can never be opened."""
    maze = Maze(3, 3)
    with pytest.raises(MazeError):
        maze.open_wall(0, 0, NORTH)
    with pytest.raises(MazeError):
        maze.open_wall(0, 0, WEST)
    with pytest.raises(MazeError):
        maze.open_wall(2, 2, SOUTH)
    with pytest.raises(MazeError):
        maze.open_wall(2, 2, EAST)


def test_open_wall_outside_maze_raises() -> None:
    """Operating on a cell outside the grid raises MazeError."""
    maze = Maze(3, 3)
    with pytest.raises(MazeError):
        maze.open_wall(7, 7, NORTH)


def test_invalid_direction_raises_maze_error() -> None:
    """An invalid direction raises MazeError, never a raw KeyError."""
    maze = Maze(3, 3)
    with pytest.raises(MazeError):
        maze.open_wall(1, 1, 3)
    with pytest.raises(MazeError):
        maze.open_wall(1, 1, 0)


def test_neighbors_center_cell() -> None:
    """A center cell has 4 neighbors with correct directions."""
    maze = Maze(3, 3)
    result = set(maze.neighbors(1, 1))
    assert result == {
        (1, 0, NORTH),
        (2, 1, EAST),
        (1, 2, SOUTH),
        (0, 1, WEST),
    }


def test_neighbors_corner_cell() -> None:
    """A corner cell only has 2 neighbors."""
    maze = Maze(3, 3)
    result = set(maze.neighbors(0, 0))
    assert result == {
        (1, 0, EAST),
        (0, 1, SOUTH),
    }
