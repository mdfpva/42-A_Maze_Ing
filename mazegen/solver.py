#!/usr/bin/env python3
"""Shortest path search over a maze."""

from collections import deque

from .maze import DIRECTIONS, LETTERS, Maze


def shortest_path(maze: Maze, start: tuple[int, int],
                  goal: tuple[int, int]) -> str | None:
    """Return the shortest path from start to goal as N/E/S/W letters."""
    queue = deque([start])
    came_from: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            letters = []
            cell = goal
            while cell != start:
                cell, direction = came_from[cell]
                letters.append(LETTERS[direction])
            return "".join(reversed(letters))
        for direction, (dx, dy, _) in DIRECTIONS.items():
            if maze.has_wall(x, y, direction):
                continue
            nxt = (x + dx, y + dy)
            if nxt not in seen:
                seen.add(nxt)
                came_from[nxt] = ((x, y), direction)
                queue.append(nxt)
    return None
