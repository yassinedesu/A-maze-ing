"""A-Maze-ing — main entry point.

Usage:
    python3 a_maze_ing.py config.txt

The program:
    1. Parses the configuration file.
    2. Generates the maze (DFS + '42' pattern + constraints).
    3. Writes the hex output file.
    4. Launches the terminal interactive display.
"""

import sys

from maze.config_parser import parse_config
from maze.generator import MazeGenerator
from maze.writer import write_output
from display.terminal import run_terminal_display


def main() -> None:
    """Run the A-Maze-ing program.

    Reads config from sys.argv[1], generates the maze, writes the output
    file, and starts the interactive terminal display.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>")
        sys.exit(1)

    config = parse_config(sys.argv[1])

    gen = MazeGenerator(
        width=config.width,
        height=config.height,
        entry=config.entry,
        exit_=config.exit_,
        seed=config.seed,
        perfect=config.perfect,
        algorithm=config.algorithm,
    )

    gen.generate()
    print(f"Algorithm     : {config.algorithm}")
    write_output(gen, config.output_file)
    print(f"Maze written to '{config.output_file}' ✓")

    run_terminal_display(gen, config)


if __name__ == "__main__":
    main()
