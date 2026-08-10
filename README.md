# A-Maze-ing — reference implementation (mandatory part)

**Note: this is a study/comparison artifact written by Claude (AI), at
the request of a student, to compare against their own finished
project. It is not meant for submission.** The student's own README
must follow the subject's Chapter VII (first italic line, Description,
Instructions, Resources with AI-usage description, config format,
algorithm choice, reusability, project management).

## Layout

- `a_maze_ing.py` — entry point: argument check, config errors,
  interaction loop (regenerate / show-hide path / rotate colours /
  quit).
- `mazegen/config.py` — parsing + validation, raises `ConfigError`.
- `mazegen/maze.py` — grid with bitmask walls (N=1 E=2 S=4 W=8, set
  bit = closed, same convention as the output file), symmetric
  `open_wall`/`close_wall`, `blocked` set.
- `mazegen/pattern.py` — the "42" as digit bitmaps, centred; empty set
  when the maze is too small (the caller prints the message).
- `mazegen/generator.py` — `MazeGenerator`: iterative recursive
  backtracker for perfect mazes; braiding + loop guarantee +
  3x3-open-area guard for the playable (Pac-Man) mode.
- `mazegen/solver.py` — BFS shortest path as N/E/S/W letters.
- `mazegen/output.py` — subject's output format (hex rows, blank
  line, entry, exit, path).
- `mazegen/render.py` — ANSI-coloured ASCII rendering.

## Design notes worth comparing

1. Library code never prints and never exits: it raises
   (`ConfigError`, `MazeError`, `OutputError`); only `a_maze_ing.py`
   talks to the user.
2. `random.Random(seed)` instance: reproducibility survives any other
   use of the global `random` module.
3. Playable mode = perfect maze + braiding (open one wall per
   dead-end, repeated until stable) with a guard that rejects any
   opening creating a fully open 3x3 block. Dead-ends enclosed by the
   "42" pockets are left alone (the analyzer tolerates them).
4. The internal representation equals the file encoding, so writing
   the output is a single f-string per cell.

## Usage

    make install
    make run          # python3 a_maze_ing.py config.txt
    make lint
    python3 -m pytest tests/
    python3 -m build --wheel   # -> dist/mazegen-1.0.0-py3-none-any.whl
