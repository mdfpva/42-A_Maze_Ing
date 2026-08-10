"""mazegen: reusable maze generation library.

Quick start::

    from mazegen import MazeGenerator, pattern_cells, shortest_path

    blocked = pattern_cells(20, 15)          # the "42" (may be empty)
    gen = MazeGenerator(20, 15, seed=42, perfect=True, blocked=blocked)
    maze = gen.generate()                    # -> Maze
    print(maze.grid[0][0])                   # wall bits of cell (0, 0)
    print(shortest_path(maze, (0, 0), (19, 14)))  # e.g. "ESSE..."

Custom parameters: ``width``/``height`` set the size, ``seed`` makes
the output reproducible, ``perfect`` selects a single-path maze
(True) or a playable looped board (False), and ``blocked`` reserves
fully closed cells.  The generated structure is a ``Maze`` whose
``grid[y][x]`` bitmasks use N=1, E=2, S=4, W=8 (set bit = closed).
"""

from .config import Config, ConfigError, parse_config
from .generator import MazeGenerator
from .maze import (
    ALL_WALLS,
    DIRECTIONS,
    EAST,
    NORTH,
    SOUTH,
    WEST,
    Maze,
    MazeError,
)
from .output import OutputError, maze_lines, write_maze
from .pattern import fits, pattern_cells
from .render import render
from .solver import shortest_path

__version__ = "1.0.0"

__all__ = [
    "ALL_WALLS",
    "Config",
    "ConfigError",
    "DIRECTIONS",
    "EAST",
    "Maze",
    "MazeError",
    "MazeGenerator",
    "NORTH",
    "OutputError",
    "SOUTH",
    "WEST",
    "fits",
    "maze_lines",
    "parse_config",
    "pattern_cells",
    "render",
    "shortest_path",
    "write_maze",
]
