*This project has been created as part of the 42 curriculum by mide-fre, raferrei.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a plain-text
configuration file, generates a maze, writes it to disk using a
hexadecimal wall encoding, and displays it in the terminal with an
interactive menu.

The generator supports two modes:

- **Perfect maze** (`PERFECT=True`): exactly one path exists between any
  two cells — an academic / lab maze, equivalent to a spanning tree.
- **Playable board** (`PERFECT=False`, the default): a board directly
  usable by a Pac-Man-like game. It is fully connected, offers several
  independent routes (loops) so a chased player always has an
  alternative, and — as a bonus — contains **no dead-ends at all**
  (a perfectly *braided* board).

Every maze also displays a visible **"42"** drawn with fully closed
cells in its centre, and the program computes and can display the
shortest path from entry to exit.

The maze-generation logic lives in a standalone, installable package
called `mazegen`, so it can be reused by a later project.

## Instructions

Requires **Python 3.10+**. All commands are wrapped in the `Makefile`:

```
make install     # create the virtualenv and install dependencies
make run         # python3 a_maze_ing.py config.txt
make test        # run the pytest test suite
make lint        # flake8 + mypy with the subject's flags
make lint-strict # flake8 + mypy --strict
make build       # build the mazegen wheel and copy it to the root
make clean       # remove caches
make fclean      # clean + remove the virtualenv and build artifacts
```

Run the program directly on any configuration file:

```
python3 a_maze_ing.py config.txt
```

Once the maze is displayed, an interactive menu allows you to:

1. Regenerate a new maze
2. Show / hide the shortest path
3. Change the wall colours
4. Quit

## Configuration file format

The configuration file contains one `KEY=VALUE` pair per line. Lines
starting with `#` are comments, and inline comments after `#` are
ignored.

| Key           | Description                        | Example              |
|---------------|------------------------------------|----------------------|
| `WIDTH`       | Maze width (number of cells)       | `WIDTH=20`           |
| `HEIGHT`      | Maze height (number of cells)      | `HEIGHT=15`          |
| `ENTRY`       | Entry coordinates `x,y`            | `ENTRY=0,0`          |
| `EXIT`        | Exit coordinates `x,y`             | `EXIT=19,14`         |
| `OUTPUT_FILE` | Output file name                   | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | Perfect maze? (optional, default False) | `PERFECT=False` |
| `SEED`        | Seed for reproducibility (optional) | `SEED=42`           |

Invalid configurations (missing keys, bad types, out-of-bounds or equal
entry/exit, entry/exit inside the "42") are reported with a clear error
message; the program never crashes on bad input.

## Maze generation algorithm

The generator uses the **iterative recursive backtracker** (a randomised
depth-first search). Starting from a free cell, it carves passages to a
random unvisited neighbour, pushing cells onto an explicit stack and
backtracking when a cell has no unvisited neighbours left:

```python
while stack:
    x, y = stack[-1]
    unvisited = [
        (nx, ny, direction)
        for nx, ny, direction in maze.neighbors(x, y)
        if (nx, ny) not in visited and (nx, ny) not in self.blocked
    ]
    if unvisited:
        nx, ny, direction = self._rng.choice(unvisited)
        maze.open_wall(x, y, direction)
        visited.add((nx, ny))
        stack.append((nx, ny))
    else:
        stack.pop()
```

**Why this algorithm.** The recursive backtracker is simple to reason
about, produces long, winding corridors well suited to a maze, and its
output is a perfect maze — the ideal starting point for the playable
mode. We chose the **iterative** form (an explicit stack) rather than
real recursion so large mazes never hit Python's recursion limit.
Randomness goes through a private `random.Random(seed)` instance, so
reproducibility is not affected by any other use of the `random` module.

**Playable mode (braiding).** When `PERFECT=False`, the perfect maze is
*braided*: every dead-end (a cell with a single open wall) gets one
extra wall opened, which simultaneously removes the dead-end and creates
a loop:

```python
if len(maze.open_directions(x, y)) != 1:
    continue
candidates = [
    direction
    for nx, ny, direction in maze.neighbors(x, y)
    if maze.has_wall(x, y, direction) and (nx, ny) not in self.blocked
]
if candidates:
    direction = self._rng.choice(candidates)
    maze.open_wall(x, y, direction)
```

This yields full connectivity, dozens of independent routes, and zero
dead-ends, which the provided `maze_analyzer.py` reports as
*bonus-grade (perfectly braided)*.

## Output file format

The maze is written row by row, one hexadecimal digit per cell. Each bit
encodes a closed wall (**N=1, E=2, S=4, W=8**; a set bit means the wall
is closed). After a blank line come three lines: the entry coordinates,
the exit coordinates, and the shortest path from entry to exit written
with the letters `N`, `E`, `S`, `W`. Every line ends with `\n`.

The internal representation is identical to this encoding, so writing a
cell is a single `f"{cell:x}"`.

## Reusable module

The generation logic is packaged as `mazegen`, built into
`mazegen-1.0.0-py3-none-any.whl` at the repository root (rebuild with
`make build`). It can be installed with `pip` and imported by any
project:

```python
from mazegen import MazeGenerator, pattern_cells, shortest_path

blocked = pattern_cells(20, 15)          # the "42" (may be empty)
maze = MazeGenerator(20, 15, seed=42,
                     perfect=False, blocked=blocked).generate()
path = shortest_path(maze, (0, 0), (19, 14))
```

Custom parameters: `width`/`height` set the size, `seed` makes the
result reproducible, `perfect` selects single-path vs playable, and
`blocked` reserves fully closed cells. The generated `Maze` exposes
`grid[y][x]` wall bitmasks and helpers such as `has_wall` and
`open_directions`; `shortest_path` returns the solution. Reuse is
permitted under the MIT licence (see `LICENSE.md`).

## The "42" pattern

The "42" is drawn from two 3x5 digit bitmaps with a one-column gap,
centred in the maze. Blocked cells keep all four walls and are never
carved into. When the maze is too small to hold the pattern, it is
omitted and a message is printed:

```python
DIGIT_4 = ("101", "101", "111", "001", "001")
DIGIT_2 = ("111", "001", "111", "100", "111")
```

## Project journey

This section documents the order in which the project was built and why
each piece was added, as a quick refresher of the design.

1. **Project setup.** Virtualenv, `Makefile`, and `flake8` + `mypy` +
   `pytest` wired in from the start, so every change was checked
   immediately.

2. **Configuration parser (`mazegen/config.py`).** A `Config` dataclass
   plus validation that raises a custom `ConfigError` instead of
   printing or exiting — the library reports problems, the `main`
   decides what to do with them. This keeps the module reusable.

3. **Maze structure (`mazegen/maze.py`).** Walls are stored as a bitmask
   per cell, using the *same* bits as the output file (N=1, E=2, S=4,
   W=8). The single source of truth for coherence is `open_wall`, which
   always opens the wall on both sides at once:

   ```python
   self.grid[y][x] &= ~direction
   self.grid[y + dy][x + dx] &= ~opposite
   ```

   The `DIRECTIONS` table maps each wall bit to its `(dx, dy)` offset and
   the opposite wall, so neighbour logic never hard-codes coordinates.

4. **Perfect generator (`mazegen/generator.py`).** The iterative
   recursive backtracker described above. It only ever calls
   `neighbors()` and `open_wall()`, which is why the solid primitives
   built in step 3 pay off here.

5. **Playable mode (braiding).** `open_directions` was added to the
   `Maze` to detect dead-ends (exactly one open wall), and `_braid`
   opens one extra wall per dead-end. Two structural rules from the
   subject were verified by measurement: no fully open 3x3 area
   (`Maze.block_is_open` / `has_open_3x3`) and at least two independent
   loops (counted as `passages - (cells - 1)`).

6. **The "42" (`mazegen/pattern.py`).** `pattern_cells` returns the set
   of blocked cells for a centred "42"; the generator skips them while
   carving and braiding, and the `main` rejects an entry/exit that lands
   inside the pattern.

7. **Solver (`mazegen/solver.py`).** A breadth-first search returns the
   shortest path as `N/E/S/W` letters. BFS explores by rings of
   increasing distance, so the first time it reaches the goal it has
   found a shortest path; a `came_from` map reconstructs the route:

   ```python
   while cell != start:
       cell, direction = came_from[cell]
       letters.append(LETTERS[direction])
   return "".join(reversed(letters))
   ```

8. **Output file (`mazegen/output.py`).** Because the internal bitmask
   equals the file encoding, each cell is written as one hex digit,
   followed by the blank line, entry, exit, and path.

9. **Visualisation and menu (`mazegen/render.py`, `a_maze_ing.py`).** An
   ANSI-coloured ASCII renderer that can overlay the solution path in a
   distinct colour, wrapped in an interactive loop (regenerate,
   show/hide path, change colours, quit) that clears the screen between
   frames and handles `EOF`/`Ctrl+C` gracefully.

10. **Packaging.** `pyproject.toml` builds the `mazegen` wheel; a
    `LICENSE.md` (MIT) allows reuse by later projects.

The whole project is covered by 23 tests across `tests/`, and both modes
are validated by the provided `maze_analyzer.py`.

## Resources

- Jamis Buck — *Maze Generation: Recursive Backtracking*.
- Walter Pullen — *Think Labyrinth* (maze classification and braiding).
- Python documentation: `random.Random`, `collections.deque`.
- Graph theory: perfect mazes as spanning trees.

**AI usage.** We used an AI assistant (Claude) as a teaching aid
throughout the project. Concretely, it was used to: explain algorithms
and design trade-offs (bitmask walls, iterative vs recursive
backtracking, instance-based RNG, braiding, BFS); review our code and
suggest cleaner or more idiomatic versions; help debug specific errors
(import mistakes, the config parsing edge cases, the screen-clearing and
EOF handling in the menu); and suggest which tests to write. All the
code was written by us; the AI acted as a reviewer and tutor rather than
an author, and every design decision is documented above so we can
defend it.

## Team and project management

**Roles.** This project was built by **mide-fre** and **raferrei**
working together (pair programming) on every part, rather than splitting
the code into separate ownership. Decisions were taken jointly and both
authors are familiar with the whole codebase.

**Planning and evolution.** We built the project in layers, always
keeping it runnable and linted: setup → config parser → maze structure →
perfect generator → playable/braided mode → the "42" → solver → output
file → visualisation and menu → packaging. Tests were added alongside
each layer, which caught regressions early.

**What was hardest.** The most challenging parts were the **maze
generation** (getting the playable mode to satisfy every structural rule
— connectivity, loops, no 3x3 open areas, no dead-ends, all while
respecting the "42") and the **solver** (implementing BFS correctly and
reconstructing the path in the right order).

**What went well / what we'd improve.** The bitmask design paid off:
because the internal representation matches the output format, the file
writer and the wall-coherence checks were trivial. If we continued, we
would add a MiniLibX graphical display and animate the generation, both
suggested as bonuses.

**Tools used.** Git, `flake8`, `mypy`, `pytest`, a `Makefile` for
automation, and the provided `maze_analyzer.py` to validate both maze
modes.
