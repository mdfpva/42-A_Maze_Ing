#!/usr/bin/env python3
"""The "42" pattern: fully closed cells drawn in the maze centre."""

# Each digit is 3 columns x 5 rows; "1" marks a blocked cell.
DIGIT_4 = ("101", "101", "111", "001", "001")
DIGIT_2 = ("111", "001", "111", "100", "111")

PATTERN_WIDTH = 7   # 3 + 1 gap + 3
PATTERN_HEIGHT = 5


def pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the set of blocked cells for a centred "42"."""
    ox = (width - PATTERN_WIDTH) // 2
    oy = (height - PATTERN_HEIGHT) // 2
    cells: set[tuple[int, int]] = set()
    for row in range(PATTERN_HEIGHT):
        for col in range(3):
            if DIGIT_4[row][col] == "1":
                cells.add((ox + col, oy + row))
            if DIGIT_2[row][col] == "1":
                cells.add((ox + 4 + col, oy + row))
    return cells
