#!/usr/bin/env python3
"""Maze generation algorithms."""

import random

from .maze import Maze


class MazeGenerator:
    """Generates mazes using the recursive backtracker algorithm."""

    def __init__(self, width: int, height: int,
                 seed: int | None = None) -> None:
        """Store dimensions and initialize the random source."""
        self.width = width
        self.height = height
        self._rng = random.Random(seed)

    def generate(self) -> Maze:
        """Carve a perfect maze and return it."""
        ...


if __name__ == "__main__":
	newmaze = MazeGenerator(1, 1, 1)
