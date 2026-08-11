#!/usr/bin/env python3
"""Maze grid structure with bitmask walls."""

# Wall bits, matching the output file format
NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8


# Each direction knows its (dx, dy) and the opposite wall
DIRECTIONS: dict[int, tuple[int, int, int]] = {
    NORTH: (0, -1, SOUTH),
    EAST: (1, 0, WEST),
    SOUTH: (0, 1, NORTH),
    WEST: (-1, 0, EAST),
}


class MazeError(Exception):
    def __init__(self, msg: str = "Unkown MazeError!") -> None:
        super().__init__(msg)


class Maze:
    def __init__(self, width: int, height: int) -> None:
        self.grid: list[list[int]] = [
            [
                NORTH | EAST | SOUTH | WEST for _ in range(width)
            ] for _ in range(height)
        ]
        self.width: int = width
        self.height: int = height

    def in_bounds(self, x: int, y: int) -> bool:
        if 0 <= x < self.width:
            if 0 <= y < self.height:
                return True
        return False

    def open_wall(self, x: int, y: int, direction: int) -> None:
        if direction not in DIRECTIONS:
            raise MazeError(f"Invalid direction: {direction}")
        if not self.in_bounds(x, y):
            raise MazeError(f"Position ({x}, {y}) out of bound!")
        dx, dy, opposite = DIRECTIONS[direction]
        if not self.in_bounds(x + dx, y + dy):
            raise MazeError("Opposite "
                            f"Position ({x + dx}, {y + dy})"
                            " out of bound!")
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~opposite

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        return bool(self.grid[y][x] & direction)

    def neighbors(self, x: int, y: int) -> list[tuple[int, int, int]]:
        """Return valid neighbors as (nx, ny, direction) tuples."""
        result = []
        for direction, (dx, dy, _) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result.append((nx, ny, direction))
        return result


    def open_directions(self, x: int, y: int) -> list[int]:
        """Return the directions whose wall is open at (x, y)."""
        directions = [NORTH, EAST, SOUTH, WEST]
        result = []
        for direction in directions:
            if not self.has_wall(x, y, direction):
                result.append(direction)
        return result
