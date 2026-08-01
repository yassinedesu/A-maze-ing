"""Maze solver module — BFS shortest-path finder.

Provides:
    bfs_solve(maze) -> list[str]
        Returns the shortest direction sequence from maze.entry to maze.exit_.
"""

from collections import deque
from typing import TYPE_CHECKING, Optional

from maze.generator import DIRECTION_DELTA, DIR_CHAR

if TYPE_CHECKING:
    from maze.generator import MazeGenerator


def bfs_solve(maze: "MazeGenerator") -> list[str]:
    """Find the shortest path from maze.entry to maze.exit_ using BFS.

    BFS explores cells level by level, guaranteeing the minimum number of
    steps. Passages are detected via has_wall(): a direction without a wall
    is a valid move.

    Args:
        maze: A MazeGenerator instance whose generate() has been called.

    Returns:
        List of single-character direction strings, e.g. ['S', 'E', 'E', 'N'].
        Returns an empty list if the exit is unreachable.

    Example:
        >>> from maze.generator import MazeGenerator
        >>> gen = MazeGenerator(10, 8, seed=1)
        >>> gen.generate()
        >>> path = bfs_solve(gen)
        >>> print("".join(path))
    """
    start = maze.entry
    goal = maze.exit_

    if start == goal:
        return []

    # parent[(x, y)] = (previous_cell, direction_char) | None for the start
    parent: dict[
        tuple[int, int],
        Optional[tuple[tuple[int, int], str]],
    ] = {start: None}

    queue: deque[tuple[int, int]] = deque([start])

    while queue:
        x, y = queue.popleft()

        if (x, y) == goal:
            return _reconstruct(parent, goal)

        for direction, (dx, dy) in DIRECTION_DELTA.items():
            if maze.has_wall(x, y, direction):
                continue
            nx, ny = x + dx, y + dy
            if maze._in_bounds(nx, ny) and (nx, ny) not in parent:
                parent[(nx, ny)] = ((x, y), DIR_CHAR[direction])
                queue.append((nx, ny))

    return []  # No path found


def _reconstruct(
    parent: dict[
        tuple[int, int],
        Optional[tuple[tuple[int, int], str]],
    ],
    goal: tuple[int, int],
) -> list[str]:
    """Reconstruct the direction path by tracing back through the parent map.

    Args:
        parent: BFS parent dictionary mapping each cell to its predecessor.
        goal: The destination cell.

    Returns:
        Ordered list of direction characters from start to goal.
    """
    path: list[str] = []
    cur: tuple[int, int] = goal

    while parent[cur] is not None:
        info = parent[cur]
        assert info is not None  # narrowing for mypy
        prev, d = info
        path.append(d)
        cur = prev

    path.reverse()
    return path
