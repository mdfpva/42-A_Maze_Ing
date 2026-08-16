"""mazegen: a reusable maze generation library.

Basic usage::

    from mazegen import MazeGenerator, pattern_cells, shortest_path

    blocked = pattern_cells(20, 15)          # the "42" (may be empty)
    maze = MazeGenerator(20, 15, seed=42,
                         perfect=False, blocked=blocked).generate()
    path = shortest_path(maze, (0, 0), (19, 14))

Parameters: width/height set the size, seed makes it reproducible,
perfect selects a single-path maze (True) or a playable looped board
(False), and blocked reserves fully closed cells. The generated Maze
exposes grid[y][x] wall bitmasks (N=1, E=2, S=4, W=8; set bit = closed).
"""

from .config import parse_config, ConfigError, Config
from .maze import Maze, MazeError, NORTH, SOUTH, EAST, WEST, DIRECTIONS
from .generator import MazeGenerator
from .render import render, path_cells
from .solver import shortest_path
from .output import write_maze, OutputError
from .pattern import pattern_cells

__all__ = [
    "parse_config",
    "ConfigError",
    "Config",
    "Maze",
    "MazeError",
    "NORTH",
    "SOUTH",
    "EAST",
    "WEST",
    "DIRECTIONS",
    "MazeGenerator",
    "render",
    "shortest_path",
    "write_maze",
    "OutputError",
    "pattern_cells",
    "path_cells"
]
