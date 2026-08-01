"""mazegen — reusable maze generation package.

Public API:
    MazeGenerator  — generates mazes using Recursive Backtracker (DFS)
    bfs_solve      — finds the shortest path between two cells
    NORTH, EAST, SOUTH, WEST — direction constants
"""

from mazegen.generator import (  # noqa: F401
    MazeGenerator,
    NORTH,
    EAST,
    SOUTH,
    WEST,
    ALL_WALLS,
    OPPOSITE,
    DIRECTION_DELTA,
    DIR_CHAR,
)
from mazegen.solver import bfs_solve  # noqa: F401

__all__ = [
    "MazeGenerator",
    "bfs_solve",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
    "ALL_WALLS",
    "OPPOSITE",
    "DIRECTION_DELTA",
    "DIR_CHAR",
]
