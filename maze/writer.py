"""Maze output writer module.

Writes the maze grid and solution to a text file using the format:
    - One hex character per cell, one line per row (uppercase)
    - Blank line separator
    - Entry coordinates  (x,y)
    - Exit  coordinates  (x,y)
    - Shortest path      (e.g. SSEENNW...)
    - Every line ends with \\n
"""

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from maze.generator import MazeGenerator


def write_output(maze: "MazeGenerator", filepath: str) -> None:
    """Write the maze to a file in the required hexadecimal format.

    Each cell value (0-15) is written as one uppercase hex character.
    After the grid, an empty line is followed by the entry coordinates,
    exit coordinates, and the shortest-path direction string.

    Args:
        maze: A MazeGenerator instance whose generate() has been called.
        filepath: Destination file path (e.g. 'maze.txt').

    Raises:
        SystemExit: On any file I/O error (prints message and exits).

    Example:
        >>> gen = MazeGenerator(20, 15, entry=(0, 0), exit_=(19, 14), seed=42)
        >>> gen.generate()
        >>> write_output(gen, 'maze.txt')
    """
    try:
        with open(filepath, "w") as f:
            # --- Grid rows ---
            for row in maze.grid:
                line = "".join(format(cell, "X") for cell in row)
                f.write(line + "\n")

            # --- Blank separator ---
            f.write("\n")

            # --- Coordinates and path ---
            ex, ey = maze.entry
            f.write(f"{ex},{ey}\n")

            ox, oy = maze.exit_
            f.write(f"{ox},{oy}\n")

            f.write("".join(maze.solution) + "\n")

    except OSError as e:
        print(
            f"Error: cannot write output file '{filepath}': {e}",
            file=sys.stderr)
        sys.exit(1)
