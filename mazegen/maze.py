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


if __name__ == "__main__":
    maze: Maze = Maze(5, 5)
    print(maze.grid)
    print()
    print(maze.in_bounds(0, 0))
    print(maze.in_bounds(1, 1))
    print(maze.in_bounds(4, 4))
    print(maze.in_bounds(5, 5))
    print(maze.in_bounds(6, 6))
    print()
    maze.open_wall(3, 3, NORTH)
    for row in maze.grid:
        print(row)
    try:
        maze.open_wall(4, 4, SOUTH)
    except MazeError as e:
        print(f"{type(e).__name__}: {e}")
    try:
        maze.open_wall(5, 5, SOUTH)
    except MazeError as e:
        print(f"{type(e).__name__}: {e}")
    print()
    for i in (1, 2, 4, 8):
        print(maze.has_wall(1, 1, i))
    print()
    for i in (1, 2, 4, 8):
        maze.open_wall(1, 1, i)
    for i in (1, 2, 4, 8):
        print(maze.has_wall(1, 1, i))
