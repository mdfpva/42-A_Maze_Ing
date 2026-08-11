#!/usr/bin/env python3

from mazegen import MazeGenerator
from mazegen import NORTH, EAST, SOUTH, WEST, DIRECTIONS


def test_same_seed_produces_same_maze():
    maze1 = MazeGenerator(10, 10, seed=42).generate()
    maze2 = MazeGenerator(10, 10, seed=42).generate()

    assert maze1.grid == maze2.grid


def test_different_seed_produces_different_maze():
    maze1 = MazeGenerator(10, 10, seed=1).generate()
    maze2 = MazeGenerator(10, 10, seed=2).generate()

    assert maze1.grid != maze2.grid


def flood_fill(maze):
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


def test_maze_is_connected():
    maze = MazeGenerator(20, 20, seed=42).generate()

    visited = flood_fill(maze)

    assert len(visited) == maze.width * maze.height


def test_perfect_maze():
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
