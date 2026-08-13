#!/usr/bin/env python3

from mazegen import MazeGenerator, Maze
from mazegen import NORTH, EAST, SOUTH, WEST, DIRECTIONS


def test_same_seed_produces_same_maze() -> None:
    maze1 = MazeGenerator(10, 10, seed=42).generate()
    maze2 = MazeGenerator(10, 10, seed=42).generate()

    assert maze1.grid == maze2.grid


def test_different_seed_produces_different_maze() -> None:
    maze1 = MazeGenerator(10, 10, seed=1).generate()
    maze2 = MazeGenerator(10, 10, seed=2).generate()

    assert maze1.grid != maze2.grid


def flood_fill(maze: Maze) -> set[tuple[int, int]]:
    visited = {(0, 0)}
    stack = [(0, 0)]

    while stack:
        x, y = stack.pop()

        for direction, (dx, dy, _) in DIRECTIONS.items():
            if maze.has_wall(x, y, direction):
                continue

            nx = x + dx
            ny = y + dy

            if (nx, ny) not in visited:
                visited.add((nx, ny))
                stack.append((nx, ny))

    return visited


def test_maze_is_connected() -> None:
    maze = MazeGenerator(20, 20, seed=42).generate()

    visited = flood_fill(maze)

    assert len(visited) == maze.width * maze.height


def test_perfect_maze() -> None:
    maze = MazeGenerator(15, 15, seed=42).generate()

    removed = 0

    for y in range(maze.height):
        for x in range(maze.width):
            for wall in (NORTH, EAST, SOUTH, WEST):
                if not maze.has_wall(x, y, wall):
                    removed += 1

    passages = removed // 2
    cells = maze.width * maze.height

    assert passages == cells - 1


def test_perfect_maze_has_dead_ends() -> None:
    """Check that the perfect maze contains dead-ends."""
    maze = MazeGenerator(
        15,
        10,
        seed=1,
        perfect=True,
    ).generate()

    dead_ends = sum(
        1
        for y in range(10)
        for x in range(15)
        if len(maze.open_directions(x, y)) == 1
    )

    assert dead_ends > 0


def test_braided_maze_has_no_dead_ends() -> None:
    """The playable (non-perfect) maze should have no dead-ends."""
    maze = MazeGenerator(15, 10, seed=1, perfect=False).generate()
    dead_ends = sum(
        1
        for y in range(10)
        for x in range(15)
        if len(maze.open_directions(x, y)) == 1
    )
    assert dead_ends == 0


def test_braided_maze_is_connected() -> None:
    """Braiding only opens walls, so the maze stays fully connected."""
    maze = MazeGenerator(15, 10, seed=1, perfect=False).generate()
    assert len(flood_fill(maze)) == maze.width * maze.height


def test_playable_mode_has_no_open_3x3() -> None:
    """The braided maze must never contain a fully-open 3x3 area."""
    for seed in range(20):
        maze = MazeGenerator(20, 15, seed=seed, perfect=False).generate()
        assert not maze.has_open_3x3()

def count_loops(maze: Maze) -> int:
    """Return passages - (cells - 1): 0 for a tree, N for N loops."""
    passages = sum(
        len(maze.open_directions(x, y))
        for y in range(maze.height) for x in range(maze.width)
    ) // 2
    cells = maze.width * maze.height
    return passages - (cells - 1)


def test_playable_mode_has_at_least_two_loops() -> None:
    """The playable board must offer >= 2 independent routes."""
    for seed in range(20):
        maze = MazeGenerator(20, 15, seed=seed, perfect=False).generate()
        assert count_loops(maze) >= 2
