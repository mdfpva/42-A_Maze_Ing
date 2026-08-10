"""Maze grid with bitmask walls (N=1, E=2, S=4, W=8, set bit = closed)."""

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

# direction -> (dx, dy, opposite wall on the neighbour side)
DIRECTIONS: dict[int, tuple[int, int, int]] = {
    NORTH: (0, -1, SOUTH),
    EAST: (1, 0, WEST),
    SOUTH: (0, 1, NORTH),
    WEST: (-1, 0, EAST),
}

LETTERS: dict[int, str] = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}


class MazeError(Exception):
    """Raised on invalid maze operations."""


class Maze:
    """A rectangular grid of cells whose walls are stored as bitmasks.

    ``grid[y][x]`` holds the wall bits of cell ``(x, y)``; a set bit
    means the wall is closed.  ``blocked`` holds cells reserved for the
    "42" pattern: they keep their 4 walls and are never carved into.
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a ``width`` x ``height`` grid with every wall closed."""
        if width < 1 or height < 1:
            raise MazeError("Maze dimensions must be positive")
        self.width = width
        self.height = height
        self.grid: list[list[int]] = [
            [ALL_WALLS] * width for _ in range(height)
        ]
        self.blocked: set[tuple[int, int]] = set()

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if ``(x, y)`` is a cell of the grid."""
        return 0 <= x < self.width and 0 <= y < self.height

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """Return True if the wall on ``direction`` of ``(x, y)`` is closed."""
        return bool(self.grid[y][x] & direction)

    def open_wall(self, x: int, y: int, direction: int) -> None:
        """Open a wall and the matching wall of the neighbour."""
        nx, ny = self._neighbour(x, y, direction)
        _, _, opposite = DIRECTIONS[direction]
        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~opposite

    def close_wall(self, x: int, y: int, direction: int) -> None:
        """Close a wall and the matching wall of the neighbour."""
        nx, ny = self._neighbour(x, y, direction)
        _, _, opposite = DIRECTIONS[direction]
        self.grid[y][x] |= direction
        self.grid[ny][nx] |= opposite

    def neighbors(self, x: int, y: int) -> list[tuple[int, int, int]]:
        """Return in-bounds neighbours of ``(x, y)`` as (nx, ny, direction)."""
        result: list[tuple[int, int, int]] = []
        for direction, (dx, dy, _) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result.append((nx, ny, direction))
        return result

    def open_directions(self, x: int, y: int) -> list[int]:
        """Return the directions whose wall is open at ``(x, y)``."""
        return [d for d in DIRECTIONS if not self.has_wall(x, y, d)]

    def _neighbour(self, x: int, y: int, direction: int) -> tuple[int, int]:
        """Validate a wall operation and return the neighbour cell."""
        if direction not in DIRECTIONS:
            raise MazeError(f"Invalid direction: {direction}")
        if not self.in_bounds(x, y):
            raise MazeError(f"Cell ({x}, {y}) out of bounds")
        dx, dy, _ = DIRECTIONS[direction]
        nx, ny = x + dx, y + dy
        if not self.in_bounds(nx, ny):
            raise MazeError("Cannot open the external border")
        return nx, ny
