"""Terminal display module — ANSI renderer and interactive menu.

Provides:
    run_terminal_display(gen, config) -> None
        Starts the interactive terminal loop after generation.
"""

import os
import sys
import time
from typing import TYPE_CHECKING

from maze.generator import (
    MazeGenerator,
    NORTH, WEST,
    DIRECTION_DELTA, DIR_CHAR,
)

if TYPE_CHECKING:
    from maze.config_parser import MazeConfig

# ---------------------------------------------------------------------------
# T-14 — Color themes
# ---------------------------------------------------------------------------
WALL_COLORS: list[tuple[str, str]] = [
    ("White",   "\033[47m"),
    ("Yellow",  "\033[43m"),
    ("Green",   "\033[42m"),
    ("Cyan",    "\033[46m"),
    ("Blue",    "\033[44m"),
    ("Magenta", "\033[45m"),
]

_RESET: str = "\033[0m"
_BG_BLACK: str = "\033[40m"
_BG_ENTRY: str = "\033[45m"
_BG_EXIT: str = "\033[41m"
_BG_PATH: str = "\033[48;5;118m"
_BG_42: str = "\033[42m"
_BG_42_DEFAULT: str = "\033[47m"

_PIXEL: str = "  "


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def _get_path_cells(gen: MazeGenerator) -> set[tuple[int, int]]:
    """Convert gen.solution into a set of (x, y) cell positions on the path.

    Args:
        gen: The maze generator with a populated solution.

    Returns:
        Set of cell coordinates on the solution path.
    """
    cells: set[tuple[int, int]] = set()
    x, y = gen.entry
    cells.add((x, y))
    for d_char in gen.solution:
        for direction, ch in DIR_CHAR.items():
            if ch == d_char:
                dx, dy = DIRECTION_DELTA[direction]
                x += dx
                y += dy
                cells.add((x, y))
                break
    return cells


def _is_passage_on_path(
    path_cells: set[tuple[int, int]],
    x1: int, y1: int,
    x2: int, y2: int,
) -> bool:
    """Return True if both cells are on the path
     (so the passage between them should be colored).

    Args:
        path_cells: Set of path cell positions.
        x1: Column of first cell.
        y1: Row of first cell.
        x2: Column of second cell.
        y2: Row of second cell.

    Returns:
        True when both cells are in path_cells.
    """
    return (x1, y1) in path_cells and (x2, y2) in path_cells


# ---------------------------------------------------------------------------
# T-12 — ANSI maze renderer
# ---------------------------------------------------------------------------

def render_maze(
    gen: MazeGenerator,
    wall_color: str = WALL_COLORS[0][1],
    show_path: bool = False,
    color_42: bool = False,
) -> None:
    """Render the maze to the terminal using ANSI background colors.

    Uses the 2N+1 strategy: a W×H maze is rendered as a
    (2W+1) × (2H+1) grid of two-space pixels.
    Path passages (between two adjacent path cells) are also colored
    so the path appears as a solid continuous line.

    Args:
        gen: The maze generator whose generate() has been called.
        wall_color: ANSI background escape code for walls.
        show_path: When True, highlight the solution path in cyan.
        color_42: When True, highlight the 42 pattern cells in green.
    """
    path_cells: set[tuple[int, int]] = (
        _get_path_cells(gen) if show_path else set()
    )
    ex, ey = gen.entry
    ox, oy = gen.exit_

    render_h = 2 * gen.height + 1
    render_w = 2 * gen.width + 1

    for ry in range(render_h):
        line_parts: list[str] = []

        for rx in range(render_w):
            col_even = (rx % 2 == 0)
            row_even = (ry % 2 == 0)

            # --- Corner: always a wall ---
            if col_even and row_even:
                line_parts.append(wall_color + _PIXEL + _RESET)

            # --- Vertical divider: west wall of cell (rx//2, cy) ---
            elif col_even and not row_even:
                cy = (ry - 1) // 2
                cell_x = rx // 2      # cell to the right of this divider
                cell_x_left = cell_x - 1  # cell to the left

                if not gen._in_bounds(cell_x, cy):
                    line_parts.append(wall_color + _PIXEL + _RESET)
                elif gen.has_wall(cell_x, cy, WEST):
                    line_parts.append(wall_color + _PIXEL + _RESET)
                elif show_path and _is_passage_on_path(
                    path_cells, cell_x_left, cy, cell_x, cy
                ):
                    line_parts.append(_BG_PATH + _PIXEL + _RESET)
                else:
                    line_parts.append(_BG_BLACK + _PIXEL + _RESET)

            # --- Horizontal divider: north wall of cell (cx, ry//2) ---
            elif not col_even and row_even:
                cx = (rx - 1) // 2
                cell_y = ry // 2       # cell below this divider
                cell_y_above = cell_y - 1  # cell above

                if not gen._in_bounds(cx, cell_y):
                    line_parts.append(wall_color + _PIXEL + _RESET)
                elif gen.has_wall(cx, cell_y, NORTH):
                    line_parts.append(wall_color + _PIXEL + _RESET)
                elif show_path and _is_passage_on_path(
                    path_cells, cx, cell_y_above, cx, cell_y
                ):
                    line_parts.append(_BG_PATH + _PIXEL + _RESET)
                else:
                    line_parts.append(_BG_BLACK + _PIXEL + _RESET)

            # --- Cell interior ---
            else:
                cx = (rx - 1) // 2
                cy = (ry - 1) // 2

                if not gen._in_bounds(cx, cy):
                    line_parts.append(wall_color + _PIXEL + _RESET)
                    continue

                if (cx, cy) in gen._42_cells:
                    bg = _BG_42 if color_42 else _BG_42_DEFAULT
                    line_parts.append(bg + _PIXEL + _RESET)
                elif (cx, cy) == (ex, ey):
                    line_parts.append(_BG_ENTRY + _PIXEL + _RESET)
                elif (cx, cy) == (ox, oy):
                    line_parts.append(_BG_EXIT + _PIXEL + _RESET)
                elif show_path and (cx, cy) in path_cells:
                    line_parts.append(_BG_PATH + _PIXEL + _RESET)
                else:
                    line_parts.append(_BG_BLACK + _PIXEL + _RESET)

        print("".join(line_parts))


# ---------------------------------------------------------------------------
# T-18 BONUS — Generation animation (terminal)
# ---------------------------------------------------------------------------

def animate_generation(
    config: "MazeConfig",
    wall_color: str,
    color_42: bool,
    delay: float = 0.03,
) -> MazeGenerator:
    """Animate the maze generation step by step in the terminal.

    Builds the maze incrementally using the DFS stack, rendering after
    each wall removal so the user can watch the algorithm carve passages.

    Args:
        config: Maze configuration (size, entry, exit, seed, algorithm).
        wall_color: ANSI color code for walls.
        color_42: Whether to highlight the 42 pattern.
        delay: Seconds to wait between each rendered step.

    Returns:
        The fully generated MazeGenerator instance.
    """
    import random as _random
    from maze.generator import ALL_WALLS

    seed = (
        config.seed if config.seed is not None else _random.randint(0, 2**31))
    rng = _random.Random(seed)

    gen = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_=config.exit_,
        seed=seed,
        perfect=config.perfect,
        algorithm=config.algorithm,
    )

    # Reset grid
    gen.grid = [[ALL_WALLS] * gen.width for _ in range(gen.height)]
    gen._rng = rng
    gen._42_cells = set()

    forbidden = gen._compute_42_cells()

    visited: list[list[bool]] = [
        [False] * gen.width for _ in range(gen.height)
    ]
    for fx, fy in forbidden:
        visited[fy][fx] = True

    sx, sy = gen.entry
    visited[sy][sx] = True
    stack: list[tuple[int, int]] = [(sx, sy)]
    step = 0

    if config.algorithm == "prim":
        """Build the initial frontier from the entry cell"""
        frontier: list[tuple[int, int, int]] = []
        for d, (dx, dy) in DIRECTION_DELTA.items():
            nx, ny = sx + dx, sy + dy
            if gen._in_bounds(nx, ny) and not visited[ny][nx]:
                frontier.append((sx, sy, d))

        while frontier:
            idx = rng.randint(0, len(frontier) - 1)
            fx, fy, d = frontier.pop(idx)
            dx, dy = DIRECTION_DELTA[d]
            nx, ny = fx + dx, fy + dy

            if not gen._in_bounds(nx, ny) or visited[ny][nx]:
                continue

            gen._remove_wall(fx, fy, d)
            visited[ny][nx] = True

            for nd, (ndx, ndy) in DIRECTION_DELTA.items():
                nnx, nny = nx + ndx, ny + ndy
                if gen._in_bounds(nnx, nny) and not visited[nny][nnx]:
                    frontier.append((nx, ny, nd))

            step += 1
            if step % 3 == 0:
                clear_screen()
                render_maze(gen, wall_color=wall_color, color_42=color_42)
                print(f"\n  Generating... ({step} steps)", end=None)
                print("  [press nothing, just watch]")
                time.sleep(delay)

    else:
        """else it will animate the recursive_backtracker (DFS)"""
        stack: list[tuple[int, int]] = [(sx, sy)]

        while stack:
            x, y = stack[-1]
            dirs = list(DIRECTION_DELTA.keys())
            rng.shuffle(dirs)

            moved = False
            for d in dirs:
                dx, dy = DIRECTION_DELTA[d]
                nx, ny = x + dx, y + dy
                if gen._in_bounds(nx, ny) and not visited[ny][nx]:
                    gen._remove_wall(x, y, d)
                    visited[ny][nx] = True
                    stack.append((nx, ny))
                    moved = True
                    break

            if not moved:
                stack.pop()

            step += 1
            if step % 3 == 0:
                clear_screen()
                render_maze(gen, wall_color=wall_color, color_42=color_42)
                print(f"\n  Generating... ({step} steps)", end=None)
                print("  [press nothing, just watch]")
                time.sleep(delay)
    return gen


# ---------------------------------------------------------------------------
# Menu helper
# ---------------------------------------------------------------------------

def _print_menu(
    wall_name: str,
    show_path: bool,
    color_42: bool,
    algorithm: str,
) -> None:
    """Print the interactive menu with current state indicators.

    Args:
        wall_name: Human-readable name of the current wall color theme.
        show_path: Current path visibility state.
        color_42: Current 42 pattern color state.
        algorithm: Currently active generation algorithm.
    """
    path_state = "ON " if show_path else "OFF"
    c42_state = "ON " if color_42 else "OFF"
    print(f"\n==== A-Maze-ing ==== [{algorithm}]")
    print("  1. Re-generate a new maze")
    print(f"  2. Show/Hide solution path     [{path_state}]")
    print(f"  3. Rotate wall color           [{wall_name}]")
    print(f"  4. Toggle '42' pattern color   [{c42_state}]")
    print("  5. Animate generation          [BONUS]")
    print("  6. Quit")
    print("Choice (1-6): ", end="", flush=True)


# ---------------------------------------------------------------------------
# T-13 — Interactive menu loop
# ---------------------------------------------------------------------------

def run_terminal_display(gen: MazeGenerator, config: "MazeConfig") -> None:
    """Start the interactive terminal display loop.

    Args:
        gen: The initial maze generator (already generated).
        config: The parsed maze configuration (used for regeneration).
    """
    wall_idx: int = 0
    show_path: bool = False
    color_42: bool = False

    clear_screen()
    render_maze(
        gen,
        wall_color=WALL_COLORS[wall_idx][1],
        show_path=show_path,
        color_42=color_42,
    )
    _print_menu(WALL_COLORS[wall_idx][0], show_path, color_42, gen.algorithm)

    while True:
        try:
            choice = input().strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            sys.exit(0)

        if choice == "1":
            import random as _random
            new_seed = _random.randint(0, 2**31)
            gen = MazeGenerator(
                width=config.width,
                height=config.height,
                entry=config.entry,
                exit_=config.exit_,
                seed=new_seed,
                perfect=config.perfect,
                algorithm=config.algorithm,
            )
            gen.generate()
            show_path = False

        elif choice == "2":
            show_path = not show_path

        elif choice == "3":
            wall_idx = (wall_idx + 1) % len(WALL_COLORS)

        elif choice == "4":
            color_42 = not color_42

        elif choice == "5":
            gen = animate_generation(
                config,
                wall_color=WALL_COLORS[wall_idx][1],
                color_42=color_42,
            )
            show_path = False

        elif choice == "6":
            print("Goodbye!")
            sys.exit(0)

        else:
            print("Invalid choice — please enter a number between 1 and 6.")
            continue

        clear_screen()
        render_maze(
            gen,
            wall_color=WALL_COLORS[wall_idx][1],
            show_path=show_path,
            color_42=color_42,
        )
        _print_menu(
            WALL_COLORS[wall_idx][0], show_path, color_42, gen.algorithm)
