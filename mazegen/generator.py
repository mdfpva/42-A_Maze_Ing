#!/usr/bin/env python3
"""Maze generation algorithms."""

import random

from .maze import Maze


class MazeGenerator:
    """Generates mazes using the recursive backtracker algorithm."""

    def __init__(self, width: int, height: int,
                 seed: int | None = None,
                 perfect: bool = True) -> None:
        """Store dimensions and initialize the random source."""
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.perfect = perfect

    def _braid(self, maze: Maze) -> None:
        """Open an extra wall from each dead-end when possible."""
        for y in range(self.height):
            for x in range(self.width):
                if len(maze.open_directions(x, y)) != 1:
                    continue

                candidates = [
                    direction
                    for nx, ny, direction in maze.neighbors(x, y)
                    if maze.has_wall(x, y, direction)
                ]

                if candidates:
                    direction = self._rng.choice(candidates)
                    maze.open_wall(x, y, direction)

    def generate(self) -> Maze:
        """Carve a perfect maze and return it."""
        maze = Maze(self.width, self.height)

        start = (0, 0)
        stack = [start]
        visited = {start}

        while stack:
            x, y = stack[-1]

            unvisited = [
                (nx, ny, direction)
                for nx, ny, direction in maze.neighbors(x, y)
                if (nx, ny) not in visited
            ]

            if unvisited:
                nx, ny, direction = self._rng.choice(unvisited)

                maze.open_wall(x, y, direction)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        if not self.perfect:
            self._braid(maze)

        return maze
