"""Maze generation: perfect mazes and playable (Pac-Man-like) boards."""

import random

from .maze import DIRECTIONS, EAST, SOUTH, Maze


class MazeGenerator:
    """Generate mazes with the iterative recursive-backtracker algorithm.

    Parameters
    ----------
    width, height:
        Maze dimensions in cells.
    seed:
        Optional seed for reproducible mazes.  A private
        ``random.Random`` instance is used so the sequence is not
        affected by other users of the ``random`` module.
    perfect:
        True for a single-path maze, False for a playable board with
        loops and (almost) no dead-ends.
    blocked:
        Cells that must keep their four walls (the "42" pattern).
    """

    def __init__(self, width: int, height: int, seed: int | None = None,
                 perfect: bool = True,
                 blocked: set[tuple[int, int]] | None = None) -> None:
        """Store the generation parameters."""
        self.width = width
        self.height = height
        self.perfect = perfect
        self.blocked = set(blocked) if blocked else set()
        self._rng = random.Random(seed)

    def generate(self) -> Maze:
        """Return a newly generated maze."""
        maze = Maze(self.width, self.height)
        maze.blocked = set(self.blocked)
        self._carve(maze)
        if not self.perfect:
            self._braid(maze)
            self._ensure_loops(maze)
        return maze

    # ------------------------------------------------------------------
    # perfect maze (spanning tree over the non-blocked cells)
    # ------------------------------------------------------------------
    def _carve(self, maze: Maze) -> None:
        """Depth-first carve a perfect maze, skipping blocked cells."""
        start = self._first_free(maze)
        stack = [start]
        visited = {start}
        while stack:
            x, y = stack[-1]
            options = [
                (nx, ny, d) for nx, ny, d in maze.neighbors(x, y)
                if (nx, ny) not in visited and (nx, ny) not in maze.blocked
            ]
            if not options:
                stack.pop()
                continue
            nx, ny, direction = self._rng.choice(options)
            maze.open_wall(x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))

    def _first_free(self, maze: Maze) -> tuple[int, int]:
        """Return the first non-blocked cell (raster order)."""
        for y in range(maze.height):
            for x in range(maze.width):
                if (x, y) not in maze.blocked:
                    return (x, y)
        raise ValueError("No free cell to start from")

    # ------------------------------------------------------------------
    # playable board: remove dead-ends, keep corridors <= 2 cells wide
    # ------------------------------------------------------------------
    def _braid(self, maze: Maze) -> None:
        """Open walls in dead-ends until none can legally be fixed.

        Several passes are needed: opening one dead-end changes the
        neighbourhood and may unlock another one that was stuck
        behind the 3x3 open-area guard.
        """
        changed = True
        while changed:
            changed = False
            dead_ends = [
                (x, y)
                for y in range(maze.height) for x in range(maze.width)
                if (x, y) not in maze.blocked
                and len(maze.open_directions(x, y)) == 1
            ]
            self._rng.shuffle(dead_ends)
            for x, y in dead_ends:
                if len(maze.open_directions(x, y)) != 1:
                    continue
                if self._open_extra_wall(maze, x, y):
                    changed = True

    def _open_extra_wall(self, maze: Maze, x: int, y: int) -> bool:
        """Open one closed wall of ``(x, y)`` without making a 3x3 area."""
        options = [
            d for nx, ny, d in maze.neighbors(x, y)
            if maze.has_wall(x, y, d) and (nx, ny) not in maze.blocked
        ]
        self._rng.shuffle(options)
        for direction in options:
            maze.open_wall(x, y, direction)
            if self._open_area_at(maze, x, y) is None:
                return True
            maze.close_wall(x, y, direction)
        return False

    def _open_area_at(self, maze: Maze,
                      x: int, y: int) -> tuple[int, int] | None:
        """Return the top-left of a fully open 3x3 block near a cell."""
        for by in range(y - 2, y + 1):
            for bx in range(x - 2, x + 1):
                if not maze.in_bounds(bx, by):
                    continue
                if not maze.in_bounds(bx + 2, by + 2):
                    continue
                if self._block_is_open(maze, bx, by):
                    return (bx, by)
        return None

    @staticmethod
    def _block_is_open(maze: Maze, bx: int, by: int) -> bool:
        """Return True if the 3x3 block at (bx, by) has no inner wall."""
        for cy in range(by, by + 3):
            for cx in range(bx, bx + 3):
                if cx < bx + 2 and maze.has_wall(cx, cy, EAST):
                    return False
                if cy < by + 2 and maze.has_wall(cx, cy, SOUTH):
                    return False
        return True

    def _ensure_loops(self, maze: Maze) -> None:
        """Guarantee at least two independent routes (two extra loops)."""
        candidates = [
            (x, y, d)
            for y in range(maze.height) for x in range(maze.width)
            if (x, y) not in maze.blocked
            for nx, ny, d in maze.neighbors(x, y)
            if maze.has_wall(x, y, d) and (nx, ny) not in maze.blocked
        ]
        self._rng.shuffle(candidates)
        while self._loop_count(maze) < 2 and candidates:
            x, y, direction = candidates.pop()
            if not maze.has_wall(x, y, direction):
                continue
            maze.open_wall(x, y, direction)
            if self._open_area_at(maze, x, y) is not None:
                maze.close_wall(x, y, direction)

    @staticmethod
    def _loop_count(maze: Maze) -> int:
        """Return passages - (cells - 1): 0 for a tree, N for N loops."""
        opened = sum(
            len(maze.open_directions(x, y))
            for y in range(maze.height) for x in range(maze.width)
        )
        passages = opened // 2
        cells = maze.width * maze.height - len(maze.blocked)
        return passages - (cells - 1)


__all__ = ["MazeGenerator", "DIRECTIONS"]
