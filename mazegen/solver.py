"""Shortest path search over an existing maze."""

from collections import deque

from .maze import DIRECTIONS, LETTERS, Maze


def shortest_path(maze: Maze, start: tuple[int, int],
                  goal: tuple[int, int]) -> str | None:
    """Return the shortest path from start to goal as N/E/S/W letters.

    Uses breadth-first search over open walls.  Returns None when the
    goal cannot be reached (e.g. a cell inside the "42" pattern).
    """
    came_from: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    queue = deque([start])
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            return _rebuild(came_from, start, goal)
        for direction, (dx, dy, _) in DIRECTIONS.items():
            if maze.has_wall(x, y, direction):
                continue
            nxt = (x + dx, y + dy)
            if nxt in seen:
                continue
            seen.add(nxt)
            came_from[nxt] = ((x, y), direction)
            queue.append(nxt)
    return None


def _rebuild(came_from: dict[tuple[int, int], tuple[tuple[int, int], int]],
             start: tuple[int, int], goal: tuple[int, int]) -> str:
    """Rebuild the letter path by walking back from the goal."""
    letters: list[str] = []
    cell = goal
    while cell != start:
        cell, direction = came_from[cell]
        letters.append(LETTERS[direction])
    return "".join(reversed(letters))
