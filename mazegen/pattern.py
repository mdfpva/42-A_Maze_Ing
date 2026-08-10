"""The "42" pattern: fully closed cells drawn in the maze centre."""

# Each digit is 3 columns x 5 rows; '1' marks a blocked cell.
DIGIT_4 = ("101", "101", "111", "001", "001")
DIGIT_2 = ("111", "001", "111", "100", "111")

PATTERN_WIDTH = 7   # 3 + 1 gap + 3
PATTERN_HEIGHT = 5
# One free cell is kept around the pattern so it never touches the
# external border (a pattern glued to the border could cut the maze
# in two and break full connectivity).
MIN_WIDTH = PATTERN_WIDTH + 2
MIN_HEIGHT = PATTERN_HEIGHT + 2


def fits(width: int, height: int) -> bool:
    """Return True if the pattern fits in a ``width`` x ``height`` maze."""
    return width >= MIN_WIDTH and height >= MIN_HEIGHT


def pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the blocked cells of a centred "42", or an empty set.

    The caller is responsible for telling the user when the pattern
    is omitted (this module never prints).
    """
    if not fits(width, height):
        return set()
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
