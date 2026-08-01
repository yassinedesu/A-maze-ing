"""Maze generator module — reusable MazeGenerator class.

Implements:
  - Recursive Backtracker (DFS) algorithm
  - Prim's algorithm (bonus)
  - '42' pattern embedding
  - No 3x3 open area constraint
  - Perfect / imperfect maze support
"""

import sys
import random
from typing import Optional

# ---------------------------------------------------------------------------
# Direction constants (bitmask)
# ---------------------------------------------------------------------------
NORTH: int = 1  # bit 0
EAST: int = 2  # bit 1
SOUTH: int = 4  # bit 2
WEST: int = 8  # bit 3
ALL_WALLS: int = 0xF

OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    SOUTH: NORTH,
    EAST: WEST,
    WEST: EAST,
}

DIRECTION_DELTA: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}

DIR_CHAR: dict[int, str] = {
    NORTH: "N",
    EAST: "E",
    SOUTH: "S",
    WEST: "W",
}

# ---------------------------------------------------------------------------
# Pixel font — "4" and "2" (5 rows × 3 cols each)
# ---------------------------------------------------------------------------
_FONT_FOUR: list[list[int]] = [
    [1, 0, 1],
    [1, 0, 1],
    [1, 1, 1],
    [0, 0, 1],
    [0, 0, 1],
]

_FONT_TWO: list[list[int]] = [
    [1, 1, 1],
    [0, 0, 1],
    [1, 1, 1],
    [1, 0, 0],
    [1, 1, 1],
]

_PAT_H: int = 5
_PAT_W: int = 7  # 3 cols + 1 gap + 3 cols
_MIN_W: int = _PAT_W + 4
_MIN_H: int = _PAT_H + 4


# ---------------------------------------------------------------------------
# MazeGenerator
# ---------------------------------------------------------------------------
class MazeGenerator:
    """Reusable maze generator using DFS or Prim's algorithm.

    Each cell stores a 4-bit wall bitmask:
        bit 0 (1) = NORTH wall closed
        bit 1 (2) = EAST  wall closed
        bit 2 (4) = SOUTH wall closed
        bit 3 (8) = WEST  wall closed
    0xF = all walls closed, 0x0 = all walls open.

    Example:
        >>> gen = MazeGenerator(20, 15, entry=(0, 0), exit_=(19, 14), seed=42)
        >>> gen.generate()
        >>> print(gen.solution)

    Args:
        width: Number of cells horizontally.
        height: Number of cells vertically.
        entry: Entry cell (x, y). Defaults to (0, 0).
        exit_: Exit cell (x, y). Defaults to (width-1, height-1).
        seed: Random seed for reproducibility. None = non-deterministic.
        perfect: True → single path between any two cells (spanning tree).
        algorithm: 'recursive_backtracker' (default) or 'prim'.
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int] = (0, 0),
        exit_: Optional[tuple[int, int]] = None,
        seed: Optional[int] = None,
        perfect: bool = True,
        algorithm: str = "recursive_backtracker",
    ) -> None:
        """Initialise MazeGenerator with dimensions and options."""
        self.width = width
        self.height = height
        self.entry = entry
        self.exit_: tuple[int, int] = (
            exit_ if exit_ is not None else (width - 1, height - 1)
        )
        self.seed = seed
        self.perfect = perfect
        self.algorithm = algorithm
        self.grid: list[list[int]] = (
            [[ALL_WALLS] * width for _ in range(height)])
        self.solution: list[str] = []
        self._42_cells: set[tuple[int, int]] = set()
        self._rng = random.Random(seed)

    # ------------------------------------------------------------------
    # Public accessors
    # ------------------------------------------------------------------

    def _in_bounds(self, x: int, y: int) -> bool:
        """Return True if (x, y) is within the maze grid.

        Args:
            x: Column index.
            y: Row index.

        Returns:
            True when 0 <= x < width and 0 <= y < height.
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def get_cell(self, x: int, y: int) -> int:
        """Return the wall bitmask of cell (x, y).

        Args:
            x: Column index.
            y: Row index.

        Returns:
            Integer bitmask (0–15).
        """
        return self.grid[y][x]

    def has_wall(self, x: int, y: int, direction: int) -> bool:
        """Check whether cell (x, y) has a wall in the given direction.

        Args:
            x: Column index.
            y: Row index.
            direction: One of NORTH, EAST, SOUTH, WEST.

        Returns:
            True if the wall is closed.
        """
        return bool(self.grid[y][x] & direction)

    # ------------------------------------------------------------------
    # Private wall helpers
    # ------------------------------------------------------------------

    def _remove_wall(self, x: int, y: int, direction: int) -> None:
        """Open the wall between (x, y)
         and its neighbour, maintaining symmetry.

        Args:
            x: Column index.
            y: Row index.
            direction: Direction of the wall to open.
        """
        self.grid[y][x] &= ~direction
        dx, dy = DIRECTION_DELTA[direction]
        nx, ny = x + dx, y + dy
        if self._in_bounds(nx, ny):
            self.grid[ny][nx] &= ~OPPOSITE[direction]

    def _add_wall(self, x: int, y: int, direction: int) -> None:
        """Close a wall between (x, y) and its neighbour, maintaining symmetry.

        Args:
            x: Column index.
            y: Row index.
            direction: Direction of the wall to close.
        """
        self.grid[y][x] |= direction
        dx, dy = DIRECTION_DELTA[direction]
        nx, ny = x + dx, y + dy
        if self._in_bounds(nx, ny):
            self.grid[ny][nx] |= OPPOSITE[direction]

    # ------------------------------------------------------------------
    # '42' pattern helpers
    # ------------------------------------------------------------------

    def _compute_42_cells(self) -> set[tuple[int, int]]:
        """Compute the set of cells that will form the '42' pattern.

        Returns:
            Set of (x, y) tuples for pattern cells.
            Empty set when the maze is too small.
        """
        if self.width < _MIN_W or self.height < _MIN_H:
            return set()

        cells: set[tuple[int, int]] = set()
        sx = (self.width - _PAT_W) // 2
        sy = (self.height - _PAT_H) // 2

        for dy, row in enumerate(_FONT_FOUR):
            for dx, val in enumerate(row):
                if val:
                    cells.add((sx + dx, sy + dy))

        gap = 1
        for dy, row in enumerate(_FONT_TWO):
            for dx, val in enumerate(row):
                if val:
                    cells.add((sx + 3 + gap + dx, sy + dy))

        return cells

    def _embed_42_pattern(self, forbidden: set[tuple[int, int]]) -> None:
        """Stamp the '42' pattern into the grid as fully closed obstacle cells.

        Args:
            forbidden: Pre-computed set of pattern cell positions.
        """
        if not forbidden:
            print(
                "Warning: maze too small to embed '42' pattern",
                file=sys.stderr,
            )
            return

        self._42_cells = forbidden

        for cx, cy in forbidden:
            self.grid[cy][cx] = ALL_WALLS

        for cx, cy in forbidden:
            for d, (ddx, ddy) in DIRECTION_DELTA.items():
                nx, ny = cx + ddx, cy + ddy
                if self._in_bounds(nx, ny) and (nx, ny) not in forbidden:
                    self.grid[ny][nx] |= OPPOSITE[d]

    # ------------------------------------------------------------------
    # DFS generation
    # ------------------------------------------------------------------

    def _generate_dfs(self, forbidden: set[tuple[int, int]]) -> None:
        """Carve passages using the iterative Recursive Backtracker (DFS).

        Args:
            forbidden: Cells to skip (e.g. the '42' pattern positions).
        """
        visited: list[list[bool]] = (
            [[False] * self.width for _ in range(self.height)])

        for fx, fy in forbidden:
            visited[fy][fx] = True

        sx, sy = self.entry
        visited[sy][sx] = True
        stack: list[tuple[int, int]] = [(sx, sy)]

        while stack:
            x, y = stack[-1]
            dirs = list(DIRECTION_DELTA.keys())
            self._rng.shuffle(dirs)

            moved = False
            for d in dirs:
                dx, dy = DIRECTION_DELTA[d]
                nx, ny = x + dx, y + dy
                if self._in_bounds(nx, ny) and not visited[ny][nx]:
                    self._remove_wall(x, y, d)
                    visited[ny][nx] = True
                    stack.append((nx, ny))
                    moved = True
                    break

            if not moved:
                stack.pop()

    # ------------------------------------------------------------------
    # Prim's generation (bonus)
    # ------------------------------------------------------------------

    def _generate_prim(self, forbidden: set[tuple[int, int]]) -> None:
        """Generate maze using Randomized Prim's algorithm.

        Maintains a frontier of candidate walls and picks one at random
        at each step. Produces cave-like mazes with shorter corridors.

        Args:
            forbidden: Cells to treat as pre-visited obstacles.
        """
        visited: list[list[bool]] = (
            [[False] * self.width for _ in range(self.height)])

        for fx, fy in forbidden:
            visited[fy][fx] = True

        sx, sy = self.entry
        visited[sy][sx] = True

        frontier: list[tuple[int, int, int]] = []
        for d, (dx, dy) in DIRECTION_DELTA.items():
            nx, ny = sx + dx, sy + dy
            if self._in_bounds(nx, ny) and not visited[ny][nx]:
                frontier.append((sx, sy, d))

        while frontier:
            idx = self._rng.randint(0, len(frontier) - 1)
            fx, fy, d = frontier.pop(idx)
            dx, dy = DIRECTION_DELTA[d]
            nx, ny = fx + dx, fy + dy

            if not self._in_bounds(nx, ny) or visited[ny][nx]:
                continue

            self._remove_wall(fx, fy, d)
            visited[ny][nx] = True

            for nd, (ndx, ndy) in DIRECTION_DELTA.items():
                nnx, nny = nx + ndx, ny + ndy
                if self._in_bounds(nnx, nny) and not visited[nny][nnx]:
                    frontier.append((nx, ny, nd))

    # ------------------------------------------------------------------
    # Imperfections (non-perfect mode)
    # ------------------------------------------------------------------

    def _add_imperfections(self, forbidden: set[tuple[int, int]]) -> None:
        """Add ~10% extra passages for a non-perfect (braided) maze.

        Args:
            forbidden: Cells to avoid (pattern cells).
        """
        target = max(1, (self.width * self.height) // 10)
        dirs = list(DIRECTION_DELTA.keys())
        added = 0
        attempts = 0

        while added < target and attempts < target * 20:
            attempts += 1
            x = self._rng.randint(0, self.width - 1)
            y = self._rng.randint(0, self.height - 1)
            if (x, y) in forbidden:
                continue
            d = self._rng.choice(dirs)
            dx, dy = DIRECTION_DELTA[d]
            nx, ny = x + dx, y + dy
            if not self._in_bounds(nx, ny) or (nx, ny) in forbidden:
                continue
            on_border = (
                (y == 0 and d == NORTH)
                or (y == self.height - 1 and d == SOUTH)
                or (x == 0 and d == WEST)
                or (x == self.width - 1 and d == EAST)
            )
            if not on_border:
                self._remove_wall(x, y, d)
                added += 1

    # ------------------------------------------------------------------
    # Border & corridor constraints
    # ------------------------------------------------------------------

    def _enforce_border_walls(self) -> None:
        """Close all external border walls to fully enclose the maze."""
        for x in range(self.width):
            self.grid[0][x] |= NORTH
            self.grid[self.height - 1][x] |= SOUTH
        for y in range(self.height):
            self.grid[y][0] |= WEST
            self.grid[y][self.width - 1] |= EAST

    def _is_3x3_open(self, ox: int, oy: int) -> bool:
        """Return True if the 3x3 block at (ox, oy) has no internal walls.

        Args:
            ox: Top-left column of the block.
            oy: Top-left row of the block.

        Returns:
            True when all 12 internal walls are open.
        """
        for y in range(oy, oy + 3):
            for x in range(ox, ox + 3):
                if x < ox + 2 and self.has_wall(x, y, EAST):
                    return False
                if y < oy + 2 and self.has_wall(x, y, SOUTH):
                    return False
        return True

    def _enforce_corridor_width(self, forbidden: set[tuple[int, int]]) -> None:
        """Add a wall in every fully open 3x3 block to limit corridor width.

        Args:
            forbidden: Pattern cells that must not be modified.
        """
        for y in range(self.height - 2):
            for x in range(self.width - 2):
                if not self._is_3x3_open(x, y):
                    continue
                candidates = [
                    (x, y, EAST),
                    (x, y, SOUTH),
                    (x + 1, y, EAST),
                    (x, y + 1, SOUTH),
                ]
                valid = [
                    (cx, cy, cd)
                    for cx, cy, cd in candidates
                    if (cx, cy) not in forbidden
                    and (
                        cx + DIRECTION_DELTA[cd][0],
                        cy + DIRECTION_DELTA[cd][1],
                    )
                    not in forbidden
                ]
                if valid:
                    cx, cy, cd = self._rng.choice(valid)
                    self._add_wall(cx, cy, cd)

    # ------------------------------------------------------------------
    # Public generate()
    # ------------------------------------------------------------------

    def generate(self) -> None:
        """Generate the maze, embed '42' pattern and compute the solution.

        Steps:
            1. Reset grid to ALL_WALLS.
            2. Pre-compute '42' pattern cell positions.
            3. Run DFS or Prim (forbidden cells treated as obstacles).
            4. Optionally add imperfections (non-perfect mode).
            5. Enforce external border walls.
            6. Embed '42' pattern and fix neighbour coherency.
            7. Eliminate fully open 3x3 areas.
            8. Solve with BFS and store path in self.solution.
        """
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]
        self._rng = random.Random(self.seed)
        self.solution = []
        self._42_cells = set()

        forbidden = self._compute_42_cells()

        if self.algorithm == "prim":
            self._generate_prim(forbidden)
        else:
            self._generate_dfs(forbidden)

        if not self.perfect:
            self._add_imperfections(forbidden)

        self._enforce_border_walls()
        self._embed_42_pattern(forbidden)
        self._enforce_corridor_width(forbidden)

        from maze.solver import bfs_solve  # noqa: PLC0415

        self.solution = bfs_solve(self)
