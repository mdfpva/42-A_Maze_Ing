# A-Maze-ing — The Incremental Build Guide

> **How this guide works.** Instead of showing each finished file, this
> guide *grows* every module a piece at a time. For each increment you
> see three things: **what we have so far**, **the piece we add now** (and
> why, at that moment), and **how the file looks after** adding it. Code
> during the increments is kept deliberately simple — no type hints, no
> docstrings, minimal guards — so the *logic* is what you see. At the end
> of each module there is a **"Final, production version"** with the full
> type hints, docstrings, and error guards the project actually ships.
>
> Read it front to back and you will reconstruct the whole project the
> way it was really built: smallest possible steps, always runnable.

---

## Contents

- [Step 0 · The empty skeleton](#step-0)
- [Module A · config.py](#module-a--configpy)
- [Module B · maze.py](#module-b--mazepy)
- [Module C · generator.py (perfect)](#module-c--generatorpy-perfect)
- [Module D · generator.py (braiding)](#module-d--braiding)
- [Module E · pattern.py (the "42")](#module-e--patternpy)
- [Module F · solver.py](#module-f--solverpy)
- [Module G · output.py](#module-g--outputpy)
- [Module H · render.py + the menu](#module-h--render--menu)
- [Step Z · Packaging and validation](#step-z)
- [Appendix · principles & defence notes](#appendix)

Legend used throughout:

```
  ┌ SO FAR ┐   the file before this increment
  ┌  ADD   ┐   the new piece, in isolation, with the reason
  ┌ RESULT ┐   the whole file after the piece is folded in
```

---

## Step 0

Before any logic, create the skeleton and the tooling. The goal is that
`make lint` and `make run` work on an almost-empty project, so every
increment afterwards can be checked immediately.

**SO FAR** — nothing but an empty folder.

**ADD** — a minimal entry point, just enough to run:

```python
# a_maze_ing.py
import sys


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt")
        return 1
    print("config:", sys.argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

**RESULT** — running it does exactly one thing:

```
$ python3 a_maze_ing.py config.txt
config: config.txt
```

Also create the venv and the lint/test tooling (see the Makefile in
Step Z). From here on, after **every** increment you would run
`make lint` — it catches a missing comma or a bad indent in seconds.

> Why start this tiny? Because a project that always runs is a sequence
> of easy changes. A project you write all at once and *then* try to run
> is one hard debugging session.

---

## Module A · config.py

We build the parser piece by piece: first the error type, then a data
holder, then reading the file, then validating each field.

### A.1 — the error type

**SO FAR** — empty file.

**ADD** — a dedicated exception. Everything the parser rejects will raise
this, so `main` can catch config problems specifically:

```python
class ConfigError(Exception):
    pass
```

**RESULT**

```python
class ConfigError(Exception):
    pass
```

Why first? Because every later piece needs something to raise. Define the
failure channel before the logic that uses it.

### A.2 — the data holder

**SO FAR**

```python
class ConfigError(Exception):
    pass
```

**ADD** — a dataclass to hold a *validated* config. This is the shape the
rest of the program consumes:

```python
from dataclasses import dataclass


@dataclass
class Config:
    width: int
    height: int
    entry_position: tuple[int, int]
    exit_position: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
```

**RESULT**

```python
from dataclasses import dataclass


class ConfigError(Exception):
    pass


@dataclass
class Config:
    width: int
    height: int
    entry_position: tuple[int, int]
    exit_position: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
```

`@dataclass` writes `__init__`, `__repr__`, `__eq__` for us. `seed` is
last because it has a default — a missing SEED means "random".

### A.3 — read the file into key/value pairs

**SO FAR** — the error type and `Config` (above).

**ADD** — a function that reads the file and collects `KEY=VALUE` pairs,
ignoring blanks and comments. No validation yet — just parsing text:

```python
def parse_config(path):
    config_dict = {}
    with open(path) as fd:
        for line in fd.read().split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "#" in line:
                line = line.split("#")[0].strip()
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            config_dict[key.strip()] = value.strip()
    return config_dict
```

**RESULT** — calling it on a config returns a plain dict:

```python
>>> parse_config("config.txt")
{'WIDTH': '20', 'HEIGHT': '15', 'ENTRY': '0,0', ...}
```

Two decisions already matter here:

- `split("#")[0]` strips an *inline* comment (`EXIT=9,9 # here`).
- `split("=", 1)` splits on the **first** `=` only, so
  `OUTPUT_FILE=a=b.txt` doesn't explode the tuple unpacking.

### A.4 — guard the file open

**SO FAR** — `parse_config` opens the file with no protection.

**ADD** — wrap the read so a missing file or a directory becomes a clean
`ConfigError`, never a traceback:

```python
    try:
        with open(path) as fd:
            text = fd.read()
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e
```

**RESULT** — the read section now looks like:

```python
def parse_config(path):
    config_dict = {}
    try:
        with open(path) as fd:
            text = fd.read()
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e
    for line in text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#")[0].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config_dict[key.strip()] = value.strip()
    return config_dict
```

`except OSError` catches the whole family: missing file, permission
denied, is-a-directory — one clause.

### A.5 — check required keys

**SO FAR** — we have a dict of whatever the file contained.

**ADD** — after building the dict, verify the mandatory keys are present,
reporting *all* missing ones together:

```python
    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in config_dict]
    if missing:
        raise ConfigError(f"Missing required keys: {', '.join(missing)}")
```

**RESULT** — a config missing `HEIGHT` and `EXIT` now fails with:

```
Missing required keys: HEIGHT, EXIT
```

### A.6 — validate integers

**SO FAR** — values are still raw strings.

**ADD** — a helper that converts to int and range-checks, raising a clear
message on failure. We group validators as static methods for tidiness:

```python
class Validate:
    @staticmethod
    def int_field(value_str, min_value, field_name):
        try:
            number = int(value_str)
        except ValueError as e:
            raise ConfigError(f"'{field_name}' must be an integer!") from e
        if number < min_value:
            raise ConfigError(f"'{field_name}' must be at least {min_value + 1}!")
        return number
```

**RESULT** — used at the end of `parse_config`:

```python
    width = Validate.int_field(config_dict["WIDTH"], 2, "WIDTH")
    height = Validate.int_field(config_dict["HEIGHT"], 2, "HEIGHT")
```

`WIDTH=abc` now yields `'WIDTH' must be an integer!` instead of a crash.

### A.7 — validate coordinates

**SO FAR** — we can validate plain ints.

**ADD** — coordinates are `x,y` and must sit inside the maze. The checks
run in a careful order (right count → both ints → non-negative → in
bounds), each assuming the previous passed:

```python
    @staticmethod
    def coordinate_field(value, max_x, max_y, field_name):
        parts = value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"Wrong amount of values in '{field_name}'!")
        try:
            x, y = int(parts[0]), int(parts[1])
        except ValueError as e:
            raise ConfigError(f"'{field_name}' must be x,y") from e
        if x < 0 or y < 0:
            raise ConfigError(f"'{field_name}' must not be negative!")
        if x >= max_x or y >= max_y:
            raise ConfigError(f"'{field_name}' out of bounds!")
        return (x, y)
```

**RESULT** — used with the already-validated width/height as bounds:

```python
    entry = Validate.coordinate_field(config_dict["ENTRY"], width, height, "ENTRY")
    exit_pos = Validate.coordinate_field(config_dict["EXIT"], width, height, "EXIT")
    if entry == exit_pos:
        raise ConfigError("ENTRY and EXIT positions must be different!")
```

Note the ordering across the whole function: width/height *first*
(they bound the coordinates), then the coordinates, then "entry ≠ exit".

### A.8 — validate the boolean (the classic trap)

**SO FAR** — everything but `PERFECT`.

**ADD** — you cannot use `bool(value)`, because `bool("False")` is
`True`. Enumerate the accepted spellings:

```python
    @staticmethod
    def bool_field(value, field_name):
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ConfigError(f"'{field_name}': value must be boolean!")
```

**RESULT**

```python
    perfect = Validate.bool_field(config_dict["PERFECT"], "PERFECT")
```

### A.9 — the optional seed, and assembling the Config

**SO FAR** — all required fields validated.

**ADD** — `SEED` is optional; when present it must be an int:

```python
    seed = None
    if "SEED" in config_dict:
        try:
            seed = int(config_dict["SEED"])
        except ValueError as e:
            raise ConfigError("'SEED' must be an integer!") from e
    return Config(width, height, entry, exit_pos,
                  config_dict["OUTPUT_FILE"], perfect, seed)
```

**RESULT** — `parse_config` now returns a fully validated `Config`.

### A — Final, production version

With type hints, docstrings, and the `MIN_WIDTH`/`MIN_HEIGHT` constants:

```python
#!/usr/bin/env python3
"""Configuration parser and validator for the maze generator."""

from dataclasses import dataclass

MIN_WIDTH = 2
MIN_HEIGHT = 2


class ConfigError(Exception):
    """Raised when the configuration file is invalid."""

    def __init__(self, message: str = "Configuration Error") -> None:
        """Initialize the exception with a message."""
        super().__init__(message)


class Validate:
    """Static methods to validate and convert configuration fields."""

    @staticmethod
    def int_field(value_str: str, min_value: int, field_name: str) -> int:
        """Validate if a string is a valid integer above the minimum."""
        try:
            number = int(value_str)
        except ValueError as e:
            raise ConfigError(f"'{field_name}' must be an integer!") from e
        if number < min_value:
            msg = f"'{field_name}' must be at least {min_value + 1}!"
            raise ConfigError(msg)
        return number

    @staticmethod
    def coordinate_field(
        value: str, max_x: int, max_y: int, field_name: str
    ) -> tuple[int, int]:
        """Validate a string as a coordinate within maze boundaries."""
        parts: list[str] = value.split(",")
        if len(parts) != 2:
            raise ConfigError(f"Wrong amount of values in '{field_name}'!")
        try:
            x = int(parts[0])
            y = int(parts[1])
        except ValueError as e:
            msg = f"'{field_name}' must be in the following format: x,y"
            raise ConfigError(msg) from e
        if x < 0 or y < 0:
            raise ConfigError(f"'{field_name}' must not be negative!")
        if x >= max_x or y >= max_y:
            msg = (
                f"'{field_name}' position ({x},{y}) is out of "
                f"the maze boundaries ({max_x}x{max_y})!"
            )
            raise ConfigError(msg)
        return (x, y)

    @staticmethod
    def bool_field(value: str, field_name: str) -> bool:
        """Validate and convert a string into a boolean value."""
        if value.lower() in ("true", "1", "yes"):
            return True
        if value.lower() in ("false", "0", "no"):
            return False
        raise ConfigError(f"'{field_name}': value must be boolean!")


@dataclass
class Config:
    """Data class representing a valid maze configuration."""

    width: int
    height: int
    entry_position: tuple[int, int]
    exit_position: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None


def parse_config(path: str) -> Config:
    """Parse a configuration file and return a valid Config object."""
    config_dict: dict[str, str] = {}
    try:
        with open(path, "r") as config_fd:
            config_text: str = config_fd.read()
    except OSError as e:
        raise ConfigError(f"Cannot read configuration file: {e}") from e

    for line in config_text.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "#" in line:
            line = line.split("#")[0].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        config_dict[key.strip()] = value.strip()

    required = ["WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"]
    missing = [k for k in required if k not in config_dict]
    if missing:
        raise ConfigError(f"Missing required keys: {', '.join(missing)}")

    width = Validate.int_field(config_dict["WIDTH"], MIN_WIDTH, "WIDTH")
    height = Validate.int_field(config_dict["HEIGHT"], MIN_HEIGHT, "HEIGHT")
    entry = Validate.coordinate_field(
        config_dict["ENTRY"], width, height, "ENTRY")
    exit_pos = Validate.coordinate_field(
        config_dict["EXIT"], width, height, "EXIT")
    if entry == exit_pos:
        raise ConfigError("ENTRY and EXIT positions must be different!")
    perfect = Validate.bool_field(config_dict["PERFECT"], "PERFECT")
    output_file = config_dict["OUTPUT_FILE"]

    seed: int | None = None
    if "SEED" in config_dict:
        try:
            seed = int(config_dict["SEED"])
        except ValueError as e:
            raise ConfigError("'SEED' must be an integer!") from e

    return Config(width, height, entry, exit_pos, output_file, perfect, seed)
```

**Wire it into `main`** — the library raises, the program decides:

```python
try:
    config = parse_config(sys.argv[1])
except ConfigError as error:
    print(f"Config error: {error}", file=sys.stderr)
    return 1
```

---

## Module B · maze.py

The structure everything else leans on. We grow it: constants → the grid
→ opening a wall → reading walls → neighbours → the derived helpers.

### B.1 — the wall bits

**SO FAR** — empty file.

**ADD** — four constants, one per wall. A **set bit means the wall is
closed**, and the values are chosen to match the output file (N=1, E=2,
S=4, W=8), so the internal number *is* the hex digit later:

```python
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
```

**RESULT**

```python
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8
```

### B.2 — the direction table

**SO FAR** — the four bits.

**ADD** — one table that maps each direction to its movement `(dx, dy)`
and the **opposite** wall on the neighbour. This single table is why no
coordinate arithmetic is ever duplicated:

```python
DIRECTIONS = {
    NORTH: (0, -1, SOUTH),
    EAST:  (1, 0, WEST),
    SOUTH: (0, 1, NORTH),
    WEST:  (-1, 0, EAST),
}
```

**RESULT**

```python
NORTH, EAST, SOUTH, WEST = 1, 2, 4, 8

DIRECTIONS = {
    NORTH: (0, -1, SOUTH),
    EAST:  (1, 0, WEST),
    SOUTH: (0, 1, NORTH),
    WEST:  (-1, 0, EAST),
}
```

Read a row like this: "to go NORTH, add `(0,-1)`; when I open my north
wall, the neighbour's matching wall is its SOUTH."

### B.3 — the grid, all walls closed

**SO FAR** — bits and the table.

**ADD** — the `Maze` class. Its grid starts with every cell fully closed
(`15` = `1111`). `grid[y][x]` — row first — will make writing the file
line by line natural:

```python
class Maze:
    def __init__(self, width, height):
        self.grid = [[NORTH | EAST | SOUTH | WEST for _ in range(width)]
                     for _ in range(height)]
        self.width = width
        self.height = height
```

**RESULT** — a fresh 3×3 maze is a wall of 15s:

```python
>>> Maze(3, 3).grid
[[15, 15, 15], [15, 15, 15], [15, 15, 15]]
```

### B.4 — in_bounds

**SO FAR** — a grid of closed cells.

**ADD** — the single definition of "is this a real cell", reused
everywhere:

```python
    def in_bounds(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
```

**RESULT**

```python
>>> m = Maze(3, 3)
>>> m.in_bounds(0, 0), m.in_bounds(3, 0), m.in_bounds(-1, 0)
(True, False, False)
```

### B.5 — open_wall (the core), first the naive body

**SO FAR** — we can make a grid and check bounds, but nothing changes
walls yet.

**ADD** — the only method that mutates walls. Start with the essential
two lines: clear the bit on this cell **and** the opposite bit on the
neighbour, so the shared wall can never disagree:

```python
    def open_wall(self, x, y, direction):
        dx, dy, opposite = DIRECTIONS[direction]
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~opposite
```

**RESULT** — opening EAST of (1,1) also opens WEST of (2,1):

```python
>>> m = Maze(3, 3)
>>> m.open_wall(1, 1, EAST)
>>> m.grid[1][1], m.grid[1][2]      # 15-2=13 ; 15-8=7
(13, 7)
```

Why `&= ~direction` and never `-= direction`? Because `&=` is
idempotent: opening an already-open wall is harmless, whereas `-=` would
corrupt the bits.

### B.6 — open_wall, add the guards

**SO FAR** — `open_wall` works but trusts its inputs. A bad direction
raises a raw `KeyError`; opening a border wall would step outside the
grid.

**ADD** — three guards: valid direction, valid cell, and the border rule
(you cannot open a wall that points off the grid):

```python
        if direction not in DIRECTIONS:
            raise MazeError(f"Invalid direction: {direction}")
        if not self.in_bounds(x, y):
            raise MazeError(f"Position ({x}, {y}) out of bound!")
        dx, dy, opposite = DIRECTIONS[direction]
        if not self.in_bounds(x + dx, y + dy):
            raise MazeError("Opposite position out of bound!")
```

**RESULT** — the method now refuses illegal moves cleanly:

```python
>>> Maze(3, 3).open_wall(0, 0, NORTH)     # points off-grid
MazeError: Opposite position out of bound!
>>> Maze(3, 3).open_wall(1, 1, 3)         # 3 is not a wall bit
MazeError: Invalid direction: 3
```

(We add a small `MazeError(Exception)` class at the top for these.)

### B.7 — has_wall

**SO FAR** — we can open walls; now we need to read them.

**ADD** — a boolean test for one wall:

```python
    def has_wall(self, x, y, direction):
        return bool(self.grid[y][x] & direction)
```

**RESULT**

```python
>>> m = Maze(3, 3); m.open_wall(1, 1, EAST)
>>> m.has_wall(1, 1, EAST), m.has_wall(1, 1, NORTH)
(False, True)
```

### B.8 — neighbors (geometry, not reachability)

**SO FAR** — we can query individual walls.

**ADD** — every in-bounds neighbour, **regardless of walls**, tagged with
the direction. This is *geometry*: "where could I carve?", not "where can
I walk?".

```python
    def neighbors(self, x, y):
        result = []
        for direction, (dx, dy, _) in DIRECTIONS.items():
            nx, ny = x + dx, y + dy
            if self.in_bounds(nx, ny):
                result.append((nx, ny, direction))
        return result
```

**RESULT** — a corner has 2 neighbours, a centre cell 4:

```python
>>> set(Maze(3, 3).neighbors(0, 0))
{(1, 0, EAST), (0, 1, SOUTH)}
```

### B.9 — open_directions (reachability)

**SO FAR** — geometry via `neighbors`.

**ADD** — the *reachability* counterpart: which walls of a cell are open.
Its length is the whole definition of a dead-end (exactly 1):

```python
    def open_directions(self, x, y):
        return [d for d in (NORTH, EAST, SOUTH, WEST)
                if not self.has_wall(x, y, d)]
```

**RESULT**

```python
>>> m = Maze(3, 3); m.open_wall(1, 1, EAST)
>>> m.open_directions(1, 1)
[2]                                   # only EAST is open
```

### B.10 — the 3×3 detectors

**SO FAR** — everything needed to generate; but the playable mode will
need to forbid fully-open 3×3 areas.

**ADD** — two geometry queries: is *this* 3×3 block fully open, and does
*any* such block exist. A 3×3 has 12 inner walls; check the EAST wall of
each non-last column and the SOUTH wall of each non-last row:

```python
    def block_is_open(self, bx, by):
        for y in range(by, by + 3):
            for x in range(bx, bx + 3):
                if x < bx + 2 and self.has_wall(x, y, EAST):
                    return False
                if y < by + 2 and self.has_wall(x, y, SOUTH):
                    return False
        return True

    def has_open_3x3(self):
        for by in range(self.height - 2):
            for bx in range(self.width - 2):
                if self.block_is_open(bx, by):
                    return True
        return False
```

**RESULT** — on a freshly generated maze you can now ask
`maze.has_open_3x3()` and get `True`/`False`. These live on `Maze`
because they are pure grid geometry, used by both the generator and the
tests.

### B — Final, production version

```python
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


LETTERS: dict[int, str] = {NORTH: "N", EAST: "E", SOUTH: "S", WEST: "W"}


class MazeError(Exception):
    """Raised on invalid maze operations."""

    def __init__(self, msg: str = "Unknown MazeError!") -> None:
        """Initialize the exception with a message."""
        super().__init__(msg)


class Maze:
    """A grid of cells whose walls are stored as bitmasks.

    ``grid[y][x]`` holds the wall bits of cell (x, y); a set bit means
    the wall is closed (N=1, E=2, S=4, W=8).
    """

    def __init__(self, width: int, height: int) -> None:
        """Create a width x height grid with every wall closed."""
        self.grid: list[list[int]] = [
            [
                NORTH | EAST | SOUTH | WEST for _ in range(width)
            ] for _ in range(height)
        ]
        self.width: int = width
        self.height: int = height

    def in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is a cell of the grid."""
        if 0 <= x < self.width:
            if 0 <= y < self.height:
                return True
        return False

    def open_wall(self, x: int, y: int, direction: int) -> None:
        """Open a wall and the matching wall of the neighbour."""
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
        """Return True if the wall on ``direction`` of (x, y) is closed."""
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

    def block_is_open(self, bx: int, by: int) -> bool:
        """Return True if the 3x3 block at (bx, by) has no inner wall."""
        for y in range(by, by + 3):
            for x in range(bx, bx + 3):
                if x < bx + 2 and self.has_wall(x, y, EAST):
                    return False
                if y < by + 2 and self.has_wall(x, y, SOUTH):
                    return False
        return True

    def has_open_3x3(self) -> bool:
        """Return True if any fully-open 3x3 block exists."""
        for by in range(self.height - 2):
            for bx in range(self.width - 2):
                if self.block_is_open(bx, by):
                    return True
        return False
```

(`LETTERS` is added here too; the solver will need it in Module F.)

---

## Module C · generator.py (perfect)

### C.1 — the class and its private RNG

**SO FAR** — empty file (but `maze.py` exists).

**ADD** — the generator class. The one non-obvious line is the **private**
random generator, which is what makes seeds reproducible:

```python
import random
from .maze import Maze


class MazeGenerator:
    def __init__(self, width, height, seed=None, perfect=True, blocked=None):
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.perfect = perfect
        self.blocked = blocked if blocked else set()
```

**RESULT** — you can construct a generator, though it can't build yet:

```python
>>> g = MazeGenerator(10, 10, seed=42)
```

Why `random.Random(seed)` and not `random.seed(seed)`? The global RNG is
shared by the whole process; a private instance owns its own stream, so
"same seed → same maze" can't be disturbed by any other code.

### C.2 — the carve loop, bare

**SO FAR** — a generator that stores parameters.

**ADD** — `generate`: an iterative depth-first carve. Push the start,
then repeatedly look at the top of the stack; if it has an unvisited
neighbour, carve to it and go deeper; otherwise backtrack (`pop`):

```python
    def generate(self):
        maze = Maze(self.width, self.height)
        stack = [(0, 0)]
        visited = {(0, 0)}
        while stack:
            x, y = stack[-1]
            unvisited = [
                (nx, ny, d)
                for nx, ny, d in maze.neighbors(x, y)
                if (nx, ny) not in visited
            ]
            if unvisited:
                nx, ny, d = self._rng.choice(unvisited)
                maze.open_wall(x, y, d)
                visited.add((nx, ny))
                stack.append((nx, ny))
            else:
                stack.pop()
        return maze
```

**RESULT** — a perfect maze. Every cell is linked in exactly once, so
there are `N-1` passages, no cycles → a spanning tree → one unique path
between any two cells.

Trace on a 2×2 (S = start): carve E, carve S, carve W, stack unwinds —
four cells, three passages, no loop.

### C.3 — respect blocked cells (forward-compatible with the "42")

**SO FAR** — the carve visits *every* cell.

**ADD** — skip cells reserved by the "42" (Module E). One extra condition
in the comprehension:

```python
            unvisited = [
                (nx, ny, d)
                for nx, ny, d in maze.neighbors(x, y)
                if (nx, ny) not in visited and (nx, ny) not in self.blocked
            ]
```

**RESULT** — with `blocked` empty (the default) nothing changes; once the
"42" provides a set, those cells are never carved into and stay fully
walled.

### C — Final (perfect part) production version

```python
#!/usr/bin/env python3
"""Maze generation algorithms."""

import random

from .maze import Maze


class MazeGenerator:
    """Generates mazes using the recursive backtracker algorithm."""

    def __init__(self, width: int, height: int,
                 seed: int | None = None,
                 perfect: bool = True,
                 blocked: set[tuple[int, int]] | None = None
                 ) -> None:
        """Store dimensions and initialize the random source."""
        self.width = width
        self.height = height
        self._rng = random.Random(seed)
        self.perfect = perfect
        self.blocked = blocked if blocked else set()

    def generate(self) -> Maze:
        """Carve a perfect maze and return it."""
        maze = Maze(self.width, self.height)
        start = (0, 0)
        stack = [start]
        visited = {start}
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
        if not self.perfect:
            self._braid(maze)
        return maze
```

(The `if not self.perfect: self._braid(maze)` line and `_braid` itself
arrive in Module D.)

---

## Module D · braiding

Turning the perfect maze into a playable board: remove every dead-end,
which simultaneously creates the loops the board needs.

### D.1 — spot the dead-ends

**SO FAR** — `generate` produces a perfect maze with many dead-ends.

**ADD** — a `_braid` method that scans the grid for dead-ends. A dead-end
is a cell with exactly one open wall:

```python
    def _braid(self, maze):
        for y in range(self.height):
            for x in range(self.width):
                if len(maze.open_directions(x, y)) != 1:
                    continue
                # ... it's a dead-end; handle below
```

**RESULT** — the skeleton walks every cell and isolates the dead-ends.

### D.2 — choose a wall to open

**SO FAR** — we can find a dead-end but do nothing with it.

**ADD** — among the dead-end's **closed** walls, pick one that leads to a
real neighbour not in the "42", and open it:

```python
                candidates = [
                    direction
                    for nx, ny, direction in maze.neighbors(x, y)
                    if maze.has_wall(x, y, direction)
                    and (nx, ny) not in self.blocked
                ]
                if candidates:
                    direction = self._rng.choice(candidates)
                    maze.open_wall(x, y, direction)
```

**RESULT** — measured on a 6×4, `seed=3`:

```
   PERFECT=True  → 4 dead-ends
   PERFECT=False → 0 dead-ends   (every one braided away)
```

Opening that extra wall both removes the trap and, because the maze was
already a tree, creates a **loop** (a second route).

### D.3 — turn braiding on only in playable mode

**SO FAR** — `_braid` exists but nothing calls it.

**ADD** — one line at the end of `generate`:

```python
        if not self.perfect:
            self._braid(maze)
```

**RESULT** — `PERFECT=False` now yields a fully-connected, dead-end-free,
multi-loop board; `PERFECT=True` is untouched.

### D — proving the rules (not code, but essential)

Two properties must hold and are verified by measurement, then locked as
tests:

- **≥2 loops.** `loops = passages − (cells − 1)`. Measured 26–37 on
  20×15 — far above 2.
- **No open 3×3.** `maze.has_open_3x3()` is `False` across 400 mazes up
  to 50×40. Braiding opens one wall per dead-end and never concentrates
  the four openings a fully-open 3×3 centre would need.

The final `_braid`, production version:

```python
    def _braid(self, maze: Maze) -> None:
        """Open an extra wall from each dead-end when possible."""
        for y in range(self.height):
            for x in range(self.width):
                if len(maze.open_directions(x, y)) != 1:
                    continue
                candidates = [
                    direction
                    for nx, ny, direction in maze.neighbors(x, y)
                    if maze.has_wall(x, y, direction)
                    and (nx, ny) not in self.blocked
                ]
                if candidates:
                    direction = self._rng.choice(candidates)
                    maze.open_wall(x, y, direction)
```

---

## Module E · pattern.py

The visible "42" of fully-closed cells in the centre.

### E.1 — the digits as data

**SO FAR** — empty file.

**ADD** — each digit as five 3-character strings, `"1"` = a blocked cell.
Storing art as strings lets you *see* the shape in the source:

```python
DIGIT_4 = ("101", "101", "111", "001", "001")
DIGIT_2 = ("111", "001", "111", "100", "111")

PATTERN_WIDTH = 7    # 3 + 1 gap + 3
PATTERN_HEIGHT = 5
```

**RESULT** — reading the two tuples row by row shows "4" and "2":

```
   █ █    ███
   █ █      █
   ███    ███
     █    █
     █    ███
```

### E.2 — does it fit?

**SO FAR** — the digit data.

**ADD** — a guard: the pattern needs room plus a margin. Below that, it is
omitted:

```python
def fits(width, height):
    return width >= 9 and height >= 7
```

**RESULT**

```python
>>> fits(20, 15), fits(6, 6)
(True, False)
```

### E.3 — map the digits to absolute cells

**SO FAR** — we know the shape and whether it fits.

**ADD** — centre the 7×5 block and convert each `"1"` to a maze cell. The
"2" is shifted `+4` columns (3 for the "4" plus the 1-cell gap):

```python
def pattern_cells(width, height):
    if not fits(width, height):
        return set()
    ox = (width - PATTERN_WIDTH) // 2
    oy = (height - PATTERN_HEIGHT) // 2
    cells = set()
    for row in range(PATTERN_HEIGHT):
        for col in range(3):
            if DIGIT_4[row][col] == "1":
                cells.add((ox + col, oy + row))
            if DIGIT_2[row][col] == "1":
                cells.add((ox + 4 + col, oy + row))
    return cells
```

**RESULT** — drawn with `#`, a 20×15 maze gets a centred "42":

```
   ......#.#.###.......
   ......#.#...#.......
   ......###.###.......
   ........#.#.........
   ........#.###.......
```

`6x6 → set()` (omitted); `20x15 → 20 cells`.

### E.4 — wire it into generation and main

**SO FAR** — `pattern_cells` returns a set; nobody uses it.

**ADD** — three connections (in `a_maze_ing.py` / the generator call):

```python
blocked = pattern_cells(config.width, config.height)   # compute the set
if not blocked:
    print("Note: maze too small for the '42' pattern; omitted.")
if config.entry_position in blocked:                   # reject bad entry
    print("Error: ENTRY is inside the '42' pattern", file=sys.stderr)
    return 1
# ... same for exit ...
maze = MazeGenerator(w, h, seed, perfect, blocked).generate()
```

**RESULT** — the generator already skips `blocked` (Module C/D), so those
cells stay fully walled. The library stays silent; `main` prints the
note and enforces the entry/exit rule.

### E — Final, production version

```python
#!/usr/bin/env python3
"""The "42" pattern: fully closed cells drawn in the maze centre."""

# Each digit is 3 columns x 5 rows; "1" marks a blocked cell.
DIGIT_4 = ("101", "101", "111", "001", "001")
DIGIT_2 = ("111", "001", "111", "100", "111")

PATTERN_WIDTH = 7   # 3 + 1 gap + 3
PATTERN_HEIGHT = 5


def fits(width: int, height: int) -> bool:
    """Return True if the "42" fits (with a one-cell margin)."""
    return width >= 9 and height >= 7


def pattern_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the set of blocked cells for a centred "42"."""
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
```

> **The centre tension.** In Pac-Man mode the centre must stay open (the
> player starts there), yet the "42" is centred too. With these exact
> digits the board's centre column lands in the 1-cell gap between "4"
> and "2", so the centre is never blocked — confirmed by the analyzer
> across sizes. Redraw the digits and you must re-check this.

---

## Module F · solver.py

Breadth-first search for the shortest path, returned as N/E/S/W letters.

### F.1 — the BFS frontier

**SO FAR** — empty file.

**ADD** — a queue-based search that fans out from the start. Using a
`deque` and `popleft` makes it breadth-first (rings of increasing
distance), which is what guarantees a *shortest* path:

```python
from collections import deque
from .maze import DIRECTIONS, LETTERS, Maze


def shortest_path(maze, start, goal):
    queue = deque([start])
    seen = {start}
    came_from = {}
    while queue:
        x, y = queue.popleft()
        for direction, (dx, dy, _) in DIRECTIONS.items():
            if maze.has_wall(x, y, direction):
                continue                       # can only walk open walls
            nxt = (x + dx, y + dy)
            if nxt not in seen:
                seen.add(nxt)
                came_from[nxt] = ((x, y), direction)
                queue.append(nxt)
    return None
```

**RESULT** — it explores the whole reachable region and records, for each
cell, where it came from and by which direction. It doesn't return a path
yet.

Contrast with the carve: the generator used a **stack** (depth-first);
the solver uses a **queue** (breadth-first). Same skeleton, opposite
end.

### F.2 — stop at the goal and rebuild the path

**SO FAR** — BFS fills `came_from` but always returns `None`.

**ADD** — when we dequeue the goal, walk `came_from` backwards collecting
letters, then reverse (we built it goal→start):

```python
        if (x, y) == goal:
            letters = []
            cell = goal
            while cell != start:
                cell, direction = came_from[cell]
                letters.append(LETTERS[direction])
            return "".join(reversed(letters))
```

(placed right after `x, y = queue.popleft()`)

**RESULT** — a real path:

```python
>>> m = MazeGenerator(10, 10, seed=1, perfect=False).generate()
>>> shortest_path(m, (0,0), (9,9))
'EEEEEEEEESSSWSESSSSS'
```

The stored `direction` is the forward move (parent→child), so it is
already the correct letter — only the final `reversed` is needed.

### F.3 — the None contract

**SO FAR** — returns a string on success, `None` if the goal is never
dequeued.

**ADD** — nothing new in code; the point is the **type**: `str | None`.
Because mypy sees it, every caller must handle `None` (unreachable goal,
e.g. inside the "42") before using the string.

**RESULT** — `main` handles it explicitly:

```python
solution = shortest_path(maze, config.entry_position, config.exit_position)
if solution is None:
    print("Error: no path between entry and exit", file=sys.stderr)
    return 1
```

### F — Final, production version

```python
#!/usr/bin/env python3
"""Shortest path search over a maze."""

from collections import deque

from .maze import DIRECTIONS, LETTERS, Maze


def shortest_path(maze: Maze, start: tuple[int, int],
                  goal: tuple[int, int]) -> str | None:
    """Return the shortest path from start to goal as N/E/S/W letters."""
    queue = deque([start])
    came_from: dict[tuple[int, int], tuple[tuple[int, int], int]] = {}
    seen = {start}
    while queue:
        x, y = queue.popleft()
        if (x, y) == goal:
            letters = []
            cell = goal
            while cell != start:
                cell, direction = came_from[cell]
                letters.append(LETTERS[direction])
            return "".join(reversed(letters))
        for direction, (dx, dy, _) in DIRECTIONS.items():
            if maze.has_wall(x, y, direction):
                continue
            nxt = (x + dx, y + dy)
            if nxt not in seen:
                seen.add(nxt)
                came_from[nxt] = ((x, y), direction)
                queue.append(nxt)
    return None
```

---

## Module G · output.py

Writing the maze in the exact format the analyzer expects.

### G.1 — build the lines

**SO FAR** — empty file.

**ADD** — a function that returns the file as a list of strings. Each row
is one `join` of hex digits — because the internal value *is* the
encoding, this is trivial:

```python
def maze_lines(maze, entry, exit_, path):
    lines = ["".join(f"{cell:x}" for cell in row) for row in maze.grid]
    lines.append("")                       # the ONE blank line
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_[0]},{exit_[1]}")
    lines.append(path)
    return lines
```

**RESULT** — on a 6×4 maze:

```
   953953
   854452
   851392
   c56c46
   (blank)
   0,0
   5,3
   EESEEESS
```

The single blank line separates the grid from the metadata. Exactly one —
an extra blank line would make `maze_analyzer.py` mis-parse the tail.

### G.2 — write to disk, safely

**SO FAR** — we can produce the lines.

**ADD** — write them, each ending in `\n`, with a `with` block and a
library-style error:

```python
class OutputError(Exception):
    pass


def write_maze(path, maze, entry, exit_, solution):
    try:
        with open(path, "w", encoding="utf-8") as handle:
            for line in maze_lines(maze, entry, exit_, solution):
                handle.write(line + "\n")
    except OSError as exc:
        raise OutputError(f"Cannot write '{path}': {exc}") from exc
```

**RESULT** — `write_maze("maze.txt", ...)` produces the file;
`maze_analyzer.py maze.txt` can now judge it. Same pattern as everywhere:
the module raises `OutputError`, `main` decides.

### G — Final, production version

```python
#!/usr/bin/env python3
"""Writing the maze to the output file (subject format)."""

from .maze import Maze


class OutputError(Exception):
    """Raised when the output file cannot be written."""


def write_maze(path: str, maze: Maze, entry: tuple[int, int],
               exit_: tuple[int, int], solution: str) -> None:
    """Write the maze to ``path`` in the subject format."""
    try:
        with open(path, "w", encoding="utf-8") as handle:
            for line in maze_lines(maze, entry, exit_, solution):
                handle.write(line + "\n")
    except OSError as exc:
        raise OutputError(f"Cannot write '{path}': {exc}") from exc


def maze_lines(maze: Maze, entry: tuple[int, int],
               exit_: tuple[int, int], path: str) -> list[str]:
    """Return the output file lines, without trailing newlines."""
    lines = [
        "".join(f"{cell:x}" for cell in row)
        for row in maze.grid
    ]
    lines.append("")
    lines.append(f"{entry[0]},{entry[1]}")
    lines.append(f"{exit_[0]},{exit_[1]}")
    lines.append(path)
    return lines
```

---

## Module H · render + menu

### H.1 — the bare ASCII maze

**SO FAR** — empty render file.

**ADD** — draw two text rows per cell row: the north walls, then the west
walls plus a blank interior; then one bottom border:

```python
from .maze import Maze, NORTH, EAST, WEST


def render(maze, entry, exit_, path=None, color=0):
    for y in range(maze.height):
        top = ""
        mid = ""
        for x in range(maze.width):
            top += "+--" if maze.has_wall(x, y, NORTH) else "+  "
            mid += ("|" if maze.has_wall(x, y, WEST) else " ") + "  "
        print(top + "+")
        print(mid + ("|" if maze.has_wall(maze.width-1, y, EAST) else " "))
    print("+--" * maze.width + "+")
```

**RESULT** — a plain black-and-white maze in the terminal.

### H.2 — mark the solution path

**SO FAR** — walls only.

**ADD** — first, a helper that lists the cells a letter-path crosses:

```python
def path_cells(entry, path):
    steps = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry
    cells = {entry}
    for letter in path:
        dx, dy = steps[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells
```

Then use it in `render` to draw `()` inside path cells:

```python
    marked = path_cells(entry, path) if path else set()
    ...
        inside = "()" if (x, y) in marked else "  "
        mid += ("|" if maze.has_wall(x, y, WEST) else " ") + inside
```

**RESULT** — the shortest path appears as a trail of `()` from entry to
exit, weaving around the "42".

### H.3 — colour

**SO FAR** — monochrome, path marked with `()`.

**ADD** — an ANSI palette indexed by `color % len(PALETTE)` (any integer
is valid, so the menu can increment forever), with the path in its own
colour:

```python
RESET = "\033[0m"
PATH_COLOR = "\033[92m"
PALETTE = ("\033[37m", "\033[33m", "\033[36m", "\033[35m", "\033[32m")
```

Wrap each printed line in `wall_color + ... + RESET`, and render a path
cell as `PATH_COLOR + "()" + wall_color`.

**RESULT** — walls take the chosen palette colour; the path stands out in
green. (See the final version below for the exact placement.)

### H.4 — the menu loop

**SO FAR** — `render` can draw everything; nothing is interactive.

**ADD** — a loop that keeps three states (maze, whether the path shows,
the colour), clears the screen each frame, and reacts to choices —
guarding `input()` against Ctrl-D/Ctrl-C:

```python
CLEAR = "\033[2J\033[H"


def interact(config):
    blocked = pattern_cells(config.width, config.height)
    show_path, color = False, 0
    maze = MazeGenerator(config.width, config.height, config.seed,
                         config.perfect, blocked).generate()
    solution = shortest_path(maze, config.entry_position,
                             config.exit_position)
    while True:
        print(CLEAR, end="")
        path = solution if show_path else None
        render(maze, config.entry_position, config.exit_position, path, color)
        print("\n1. Regenerate  2. Show/Hide path  3. Change color  4. Quit")
        try:
            choice = input("Choice? ").strip()
        except (EOFError, KeyboardInterrupt):
            print(); break
        if choice == "1":
            maze = MazeGenerator(config.width, config.height, None,
                                 config.perfect, blocked).generate()
            solution = shortest_path(maze, config.entry_position,
                                     config.exit_position)
        elif choice == "2":
            show_path = not show_path
        elif choice == "3":
            color += 1
        elif choice == "4":
            break
        else:
            print("Invalid choice.")
```

**RESULT** — the interactive program. Two subtle points: **Regenerate
passes `seed=None`** (a fixed seed would repeat the same maze), and the
`try/except` stops Ctrl-D from crashing with `EOFError`.

### H — Final render.py, production version

```python
#!/usr/bin/env python3
"""ASCII rendering utilities."""

from .maze import Maze, NORTH, EAST, WEST


RESET = "\033[0m"
PATH_COLOR = "\033[92m"
PALETTE = ("\033[37m", "\033[33m", "\033[36m", "\033[35m", "\033[32m")


def path_cells(
        entry: tuple[int, int],
        path: str
        ) -> set[tuple[int, int]]:
    """Return the set of cells crossed by a letter path from entry."""
    steps = {"N": (0, -1), "E": (1, 0), "S": (0, 1), "W": (-1, 0)}
    x, y = entry
    cells = {entry}
    for letter in path:
        dx, dy = steps[letter]
        x, y = x + dx, y + dy
        cells.add((x, y))
    return cells


def render(
        maze: Maze,
        entry: tuple[int, int],
        exit_: tuple[int, int],
        path: str | None = None,
        color: int = 0
        ) -> None:
    """Print a rough ASCII view of the maze."""
    wall_color = PALETTE[color % len(PALETTE)]
    marked = path_cells(entry, path) if path else set()
    for y in range(maze.height):
        top = ""
        mid = ""
        for x in range(maze.width):
            top += "+--" if maze.has_wall(x, y, NORTH) else "+  "
            if (x, y) in marked:
                inside = PATH_COLOR + "()" + wall_color
            else:
                inside = "  "
            mid += ("|" if maze.has_wall(x, y, WEST) else " ") + inside
        print(wall_color + top + "+" + RESET)
        east = "|" if maze.has_wall(maze.width - 1, y, EAST) else " "
        print(wall_color + mid + east + RESET)
    print(wall_color + "+--" * maze.width + "+" + RESET)
```

The full `a_maze_ing.py` (argument check → config → "42" checks →
generate → solve → write → `interact`) is assembled from these pieces;
`main` is the only place that prints and sets exit codes.

---

## Step Z · packaging and validation

The core is done and incremental; the finishing steps are mechanical.

### Z.1 — the public API

**SO FAR** — modules exist but users would import from deep paths.

**ADD** — `mazegen/__init__.py` re-exports the useful names and carries
the module's usage docstring (which doubles as the required "short
documentation"):

```python
"""mazegen: a reusable maze generation library.

    from mazegen import MazeGenerator, pattern_cells, shortest_path
    blocked = pattern_cells(20, 15)
    maze = MazeGenerator(20, 15, seed=42,
                         perfect=False, blocked=blocked).generate()
    path = shortest_path(maze, (0, 0), (19, 14))
"""

from .config import parse_config, ConfigError, Config
from .maze import Maze, MazeError, NORTH, SOUTH, EAST, WEST, DIRECTIONS
from .generator import MazeGenerator
from .render import render, path_cells
from .solver import shortest_path
from .output import write_maze, OutputError
from .pattern import pattern_cells
```

**RESULT** — users write `from mazegen import MazeGenerator`.

### Z.2 — the build metadata

**ADD** — `pyproject.toml`, packaging *only* `mazegen/`:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "mazegen"
version = "1.0.0"
requires-python = ">=3.10"
license = { text = "MIT" }
authors = [{ name = "mide-fre" }, { name = "raferrei" }]

[tool.setuptools]
packages = ["mazegen"]
```

**RESULT** — `make build` produces
`mazegen-1.0.0-py3-none-any.whl`, copied to the repo root.

### Z.3 — prove the wheel works in isolation

**ADD** — the exact test an evaluator runs:

```bash
python3 -m venv /tmp/testpkg
/tmp/testpkg/bin/pip install ./mazegen-1.0.0-py3-none-any.whl
/tmp/testpkg/bin/python3 -c "
from mazegen import MazeGenerator, pattern_cells, shortest_path
m = MazeGenerator(15, 11, seed=1, perfect=False,
                  blocked=pattern_cells(15, 11)).generate()
print(shortest_path(m, (0,0), (14,10)))
"
```

**RESULT** — it prints a path from a *clean* venv → the module is truly
reusable.

### Z.4 — LICENSE.md

**ADD** — an MIT licence naming both authors. MIT is permissive: reuse,
modify, redistribute, keeping only the notice — exactly what "allow reuse
by later projects" asks, without the copyleft obligations of GPL.

### Z.5 — validate both modes

```bash
python3 a_maze_ing.py config.txt        # writes maze.txt
python3 maze_analyzer.py maze.txt
```

Expected:

```
 PERFECT=False → Pac-Man-USABLE ... no real dead-end -> bonus-grade
 PERFECT=True  → PERFECT maze: a single path, no loop
 (both)        → Wall coherence: OK ; Corners + centre: all reachable
```

---

## Appendix

### The build order at a glance

```
 Step 0  skeleton that runs
 A  config.py    parse + validate      (raise ConfigError)
 B  maze.py      grid, open_wall, helpers
 C  generator    iterative carve       (perfect maze)
 D  braiding     remove dead-ends      (playable board)
 E  pattern.py   the "42"              (blocked cells)
 F  solver.py    BFS shortest path
 G  output.py    hex file
 H  render+menu  ASCII, colour, loop
 Z  package + licence + validate
```

Each step left the project runnable and linted.

### Seven principles that recur

1. **Library raises, `main` decides.** No module prints or exits.
2. **One source of truth.** `open_wall` is the only wall mutator, both
   sides at once → coherence is structural.
3. **Honest primitives, constraints in the algorithm.** The "42" is a
   generator restriction, not a lie told by `Maze`.
4. **Measure, don't assume.** 3×3 and loop rules verified over hundreds
   of mazes, then locked as tests.
5. **Reproducibility via an instance RNG.** `random.Random(seed)`.
6. **Internal representation = output format.** The bitmask is the hex
   digit.
7. **Lint and test after every increment.** The test count is a signal.

### Defence cheat-sheet

- **Iterative not recursive?** Deep carves would exceed Python's
  recursion limit; the explicit stack won't.
- **`random.Random(seed)`?** Private stream, immune to other `random`
  users → reproducible.
- **Wall coherence?** All changes go through `open_wall`, both sides;
  analyzer confirms.
- **Playable ≠ perfect minus one wall?** Braiding removes *every*
  dead-end → many loops.
- **No 3×3?** One opening per dead-end never fills a block; 0/400
  measured.
- **BFS shortest?** Distance-ring expansion; goal first hit optimally.
- **Reusable how?** `pip install` the wheel; `generate()` → `Maze`;
  `shortest_path` → solution.
- **Why MIT?** Permissive reuse, no copyleft burden on later projects.

### Pitfalls and how to read the error

| symptom | cause | fix |
|---------|-------|-----|
| `command not found: mypy` | venv not active | `source .venv/bin/activate` |
| `bool("False")` is `True` | strings are truthy | enumerate accepted words |
| unpack error on `=` | `split("=")` | `split("=", 1)` |
| `KeyError: 3` in open_wall | unguarded direction | validate vs `DIRECTIONS` |
| analyzer mis-parses tail | extra blank line | exactly one blank line |
| `EOFError` in menu | unguarded `input()` | wrap in try/except |
| test count drops silently | a test was lost | watch the total |
