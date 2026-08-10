"""Tests for the mazegen reference implementation."""

import pytest

from mazegen import (
    EAST,
    Maze,
    MazeError,
    MazeGenerator,
    NORTH,
    SOUTH,
    WEST,
    pattern_cells,
    shortest_path,
)


def reachable(maze: Maze, start: tuple[int, int]) -> set[tuple[int, int]]:
    """Flood fill through open walls from ``start``."""
    seen = {start}
    stack = [start]
    while stack:
        x, y = stack.pop()
        for nx, ny, direction in maze.neighbors(x, y):
            if maze.has_wall(x, y, direction) or (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            stack.append((nx, ny))
    return seen


def open_count(maze: Maze) -> int:
    """Number of open passages in the maze."""
    total = 0
    for y in range(maze.height):
        for x in range(maze.width):
            total += len(maze.open_directions(x, y))
    return total // 2


def test_open_wall_symmetry_and_border() -> None:
    """Walls open on both sides; the border can never open."""
    maze = Maze(4, 4)
    maze.open_wall(1, 1, EAST)
    assert not maze.has_wall(1, 1, EAST)
    assert not maze.has_wall(2, 1, WEST)
    with pytest.raises(MazeError):
        maze.open_wall(0, 0, NORTH)
    with pytest.raises(MazeError):
        maze.open_wall(3, 3, SOUTH)
    with pytest.raises(MazeError):
        maze.open_wall(1, 1, 5)


def test_perfect_maze_with_pattern() -> None:
    """Perfect mode: tree over free cells, pattern fully closed."""
    blocked = pattern_cells(20, 15)
    assert blocked
    maze = MazeGenerator(20, 15, seed=7, blocked=blocked).generate()
    free = 20 * 15 - len(blocked)
    assert len(reachable(maze, (0, 0))) == free
    assert open_count(maze) == free - 1
    for x, y in blocked:
        assert maze.grid[y][x] == 0b1111


def test_reproducibility() -> None:
    """Same seed, same maze; different seed, different maze."""
    first = MazeGenerator(12, 12, seed=1).generate()
    second = MazeGenerator(12, 12, seed=1).generate()
    third = MazeGenerator(12, 12, seed=2).generate()
    assert first.grid == second.grid
    assert first.grid != third.grid


def test_playable_board() -> None:
    """Playable mode: connected, >=2 loops, few dead-ends, no 3x3."""
    blocked = pattern_cells(20, 15)
    gen = MazeGenerator(20, 15, seed=3, perfect=False, blocked=blocked)
    maze = gen.generate()
    free = 20 * 15 - len(blocked)
    assert len(reachable(maze, (0, 0))) == free
    loops = open_count(maze) - (free - 1)
    assert loops >= 2
    dead_ends = 0
    for y in range(15):
        for x in range(20):
            if (x, y) in blocked:
                continue
            if len(maze.open_directions(x, y)) != 1:
                continue
            walled = [
                (nx, ny) for nx, ny, d in maze.neighbors(x, y)
                if maze.has_wall(x, y, d)
            ]
            if all(cell in blocked for cell in walled):
                continue  # pocket enclosed by the "42": tolerated
            dead_ends += 1
    assert dead_ends <= 2
    for by in range(13):
        for bx in range(18):
            assert not MazeGenerator._block_is_open(maze, bx, by)


def test_solver_finds_shortest_path() -> None:
    """BFS returns a valid path in a trivial 1x3 corridor."""
    maze = Maze(3, 1)
    maze.open_wall(0, 0, EAST)
    maze.open_wall(1, 0, EAST)
    assert shortest_path(maze, (0, 0), (2, 0)) == "EE"
    assert shortest_path(maze, (2, 0), (0, 0)) == "WW"
