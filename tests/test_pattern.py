#!/usr/bin/env python3
"""Tests for the "42" pattern."""

from mazegen import MazeGenerator
from mazegen.pattern import pattern_cells, fits


def test_pattern_has_expected_cells() -> None:
    """A 20x15 maze has a 20-cell "42" pattern."""
    assert len(pattern_cells(20, 15)) == 20


def test_pattern_omitted_when_too_small() -> None:
    """Small mazes get no pattern."""
    assert pattern_cells(6, 6) == set()
    assert not fits(6, 6)
    assert fits(20, 15)


def test_pattern_cells_stay_closed() -> None:
    """Blocked cells keep all four walls after generation."""
    blocked = pattern_cells(20, 15)
    maze = MazeGenerator(20, 15, seed=1, perfect=False,
                         blocked=blocked).generate()
    for x, y in blocked:
        assert maze.grid[y][x] == 15   # 0b1111, all walls closed


def test_pattern_does_not_block_reachability() -> None:
    """Non-pattern cells remain reachable around the "42"."""
    blocked = pattern_cells(20, 15)
    maze = MazeGenerator(20, 15, seed=1, perfect=False,
                         blocked=blocked).generate()
    # flood fill from (0,0) should reach every non-blocked cell
    seen = {(0, 0)}
    stack = [(0, 0)]
    while stack:
        x, y = stack.pop()
        for nx, ny, d in maze.neighbors(x, y):
            if maze.has_wall(x, y, d) or (nx, ny) in seen:
                continue
            seen.add((nx, ny))
            stack.append((nx, ny))
    free = 20 * 15 - len(blocked)
    assert len(seen) == free
