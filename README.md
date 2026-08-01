*This project has been created as part of the 42 curriculum by \<login1\>, \<login2\>.*

---

## Description

**A-Maze-ing** is a Python maze generator and interactive terminal viewer.

It generates random mazes of configurable size using the **Recursive Backtracker (DFS)**
algorithm, embeds a hidden **"42"** pattern made of obstacle cells, computes the shortest
path from entry to exit using **BFS**, and displays the result in a colorful ANSI terminal
interface.

Key features:
- Perfect mazes (single path between any two cells) or braided mazes (extra passages)
- Reproducible generation via a configurable seed
- "42" pixel-font pattern embedded as fully closed obstacle cells
- No corridor wider than 2 cells (3×3 open area prevention)
- Interactive terminal: regenerate, show/hide path, cycle wall colors, toggle 42 pattern
- Reusable `mazegen` pip package for use in other projects

---

## Instructions

### Requirements

- Python 3.10 or later
- `flake8` and `mypy` (installed via `make install`)

### Install

```bash
git clone <your-repo-url>
cd amazing
make install
```

### Run

```bash
make run
# equivalent to: python3 a_maze_ing.py config.txt
```

### Other Makefile targets

```bash
make debug        # run with Python debugger (pdb)
make lint         # flake8 + mypy with strict flags
make lint-strict  # flake8 + mypy --strict
make clean        # remove __pycache__ and .mypy_cache
```

---

## Configuration File Format

The configuration file uses one `KEY=VALUE` pair per line.
Lines starting with `#` are comments and are ignored.

| Key           | Required | Type    | Description                          | Example            |
|---------------|----------|---------|--------------------------------------|--------------------|
| `WIDTH`       | ✅       | int     | Number of cells horizontally         | `WIDTH=20`         |
| `HEIGHT`      | ✅       | int     | Number of cells vertically           | `HEIGHT=15`        |
| `ENTRY`       | ✅       | x,y     | Entry cell coordinates               | `ENTRY=0,0`        |
| `EXIT`        | ✅       | x,y     | Exit cell coordinates                | `EXIT=19,14`       |
| `OUTPUT_FILE` | ✅       | string  | Output file path                     | `OUTPUT_FILE=maze.txt` |
| `PERFECT`     | ✅       | bool    | True = single path (perfect maze)    | `PERFECT=True`     |
| `SEED`        | ❌       | int     | Random seed (omit for random result) | `SEED=42`          |
| `ALGORITHM`   | ❌       | string  | `recursive_backtracker` or `prim`    | `ALGORITHM=prim`   |

Example `config.txt`:

```
# A-Maze-ing default configuration
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
```

---

## Maze Generation Algorithm

### Recursive Backtracker (DFS) — default

The maze is modeled as a graph where each cell is a node and each carved passage is an edge.
The Recursive Backtracker performs an iterative Depth-First Search:

1. Start at the entry cell, mark it visited, push it onto a stack
2. Peek at the top of the stack — find all unvisited neighbors
3. If found: choose one randomly, carve the wall between them, push the neighbor
4. If none: pop the stack (backtrack)
5. Repeat until the stack is empty

The result is a **spanning tree** of the grid graph — a perfect maze with exactly one
path between any two cells.

**Why this algorithm?**
- Simple to implement correctly and test
- Produces mazes with long, winding corridors (visually satisfying)
- Naturally iterative (no Python recursion limit issues)
- Deterministic with a seed

### Prim's Algorithm — bonus (`ALGORITHM=prim`)

Maintains a frontier of candidate walls and picks one at random at each step.
Produces shorter, bushier corridors — a "cave-like" style visually distinct from DFS.

---

## Code Reusability — `mazegen` package

The maze generation logic is packaged as a standalone pip package.

### Install

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen import MazeGenerator, bfs_solve

# Create and generate a 20×15 perfect maze, reproducible with seed 42
gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit_=(19, 14),
    seed=42,
    perfect=True,
)
gen.generate()

# Access the grid (list of lists of int, 0–15)
print(gen.grid[0])          # first row, hex bitmasks

# Check walls
from mazegen import NORTH, EAST
print(gen.has_wall(0, 0, NORTH))   # True (border wall)

# Access the solution path
print("".join(gen.solution))       # e.g. "SSEENNEESS..."

# Run BFS independently
path = bfs_solve(gen)
print(len(path))                   # number of steps
```

### Rebuild the package from source

```bash
cd mazegen-1.0.0
pip install build
python -m build
# Output: dist/mazegen-1.0.0-py3-none-any.whl
```

---

## Team & Project Management

### Roles

| Member   | Responsibilities                                      |
|----------|-------------------------------------------------------|
| \<login1\> | Makefile, DFS algorithm, output writer, ANSI renderer, pip package |
| \<login2\> | Config parser, data structure, BFS solver, "42" pattern, menu loop |

### Planning

**Day 1** — Project setup, Makefile, config parser, main skeleton  
**Day 2** — MazeGenerator class, DFS algorithm, BFS solver  
**Day 3** — "42" pattern, corridor constraint, output writer, wiring  
**Day 4** — ANSI renderer, interactive menu, color themes  
**Day 6** — pip package, README, final polish, bonuses  

The original plan included an MLX graphical display (Day 5) which was replaced by
an extended terminal display with additional color themes and bonus algorithms.

### What worked well

- Defining direction constants as bitmasks early on simplified every wall operation
- Iterative DFS avoided recursion limit issues on large mazes
- Pre-marking "42" cells as visited before DFS kept pattern integrity effortlessly

### What could be improved

- The 3×3 constraint check runs after generation; integrating it into DFS would be cleaner
- More unit tests on edge cases (1×1 maze, entry == border corner, etc.)

### Tools used

- `mypy` and `flake8` for continuous type and style checking
- `pytest` for unit testing (not submitted)
- Claude (AI) for sprint planning, ticket breakdown, and code review support
  - Used for: generating the Scrum sprint document, reviewing algorithm correctness,
    explaining BFS/DFS theory, and suggesting the "2N+1" rendering approach

---

## Resources

- [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
- [Recursive Backtracker — The Coding Train (video)](https://www.youtube.com/watch?v=Y37-gB83HKE)
- [BFS Pathfinding — Red Blob Games](https://www.redblobgames.com/pathfinding/a-star/introduction.html)
- [Python Bitwise Operators — Real Python](https://realpython.com/python-bitwise-operators/)
- [Python Packaging Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/)
- [ANSI Escape Codes — Colors](https://en.wikipedia.org/wiki/ANSI_escape_code#Colors)
- [mypy cheat sheet](https://mypy.readthedocs.io/en/stable/cheat_sheet_py3.html)