import sys
from dataclasses import dataclass
from typing import Optional


@dataclass
class MazeConfig:
    """Holds all validated maze generation parameters.

    Attributes:
        width: Number of columns in the maze.
        height: Number of rows in the maze.
        entry: (x, y) coordinates of the entry cell.
        exit_: (x, y) coordinates of the exit cell.
        output_file: Path to write the hex output.
        perfect: If True, generate a perfect maze (unique path).
        seed: Optional RNG seed for reproducibility.
        algorithm: Generation algorithm to use.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit_: tuple[int, int]
    output_file: str
    perfect: bool
    seed: Optional[int] = None
    algorithm: str = "recursive_backtracker"


def _parse_coord(value: str, key: str) -> tuple[int, int]:
    """Parse a 'x,y' string into a tuple of two ints.

    Args:
        value: The raw string from the config file, e.g. '0,0'.
        key: The config key name, used in error messages.

    Returns:
        A (x, y) integer tuple.
    """
    try:
        parts = value.split(",", 1)
        if len(parts) != 2:
            raise ValueError
        return (int(parts[0].strip()), int(parts[1].strip()))
    except ValueError:
        print(
            f"Error: '{key}' must be in 'x,y' format with integers, "
            f"got '{value}'"
        )
        sys.exit(1)


def _load_raw(path: str) -> dict[str, str]:
    """Read a KEY=VALUE config file, ignoring comments and blank lines.

    Args:
        path: Path to the config file.

    Returns:
        A dict mapping uppercase keys to their raw string values.
    """
    try:
        result: dict[str, str] = {}
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    result[key.strip().upper()] = value.strip()
        return result
    except FileNotFoundError:
        print(f"Error: config file '{path}' not found")
        sys.exit(1)


def parse_config(path: str) -> MazeConfig:
    """Parse and validate a maze config file, returning a MazeConfig.

    Args:
        path: Path to the config file.

    Returns:
        A fully validated MazeConfig dataclass instance.
    """
    data = _load_raw(path)

    # --- Check all mandatory keys are present ---
    required = {"WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE", "PERFECT"}
    for key in required:
        if key not in data:
            print(f"Error: missing required key '{key}'")
            sys.exit(1)

    # --- Parse WIDTH and HEIGHT ---
    try:
        width = int(data["WIDTH"])
        height = int(data["HEIGHT"])
    except ValueError:
        print("Error: 'WIDTH' and 'HEIGHT' must be integers")
        sys.exit(1)

    if width <= 0 or height <= 0:
        print(
            f"Error: WIDTH and HEIGHT must be > 0, "
            f"got WIDTH={width}, HEIGHT={height}"
        )
        sys.exit(1)

    # --- Parse ENTRY and EXIT ---
    entry = _parse_coord(data["ENTRY"], "ENTRY")
    exit_ = _parse_coord(data["EXIT"], "EXIT")

    # --- Bounds checks ---
    if not (0 <= entry[0] < width and 0 <= entry[1] < height):
        print(f"Error: ENTRY {entry} is out of bounds "
              f"for a {width}x{height} maze")
        sys.exit(1)

    if not (0 <= exit_[0] < width and 0 <= exit_[1] < height):
        print(f"Error: EXIT {exit_} is out of bounds "
              f"for a {width}x{height} maze")
        sys.exit(1)

    # --- Entry != Exit ---
    if entry == exit_:
        print("Error: ENTRY and EXIT must be different")
        sys.exit(1)

    # --- Parse PERFECT ---
    perfect_raw = data["PERFECT"]
    if perfect_raw == "True":
        perfect = True
    elif perfect_raw == "False":
        perfect = False
    else:
        print(f"Error: 'PERFECT' must be 'True' or 'False', "
              f"got '{perfect_raw}'")
        sys.exit(1)

    # --- Parse optional SEED ---
    seed: Optional[int] = None
    if "SEED" in data:
        try:
            seed = int(data["SEED"])
        except ValueError:
            print(f"Error: 'SEED' must be an integer, got '{data['SEED']}'")
            sys.exit(1)

    # --- Parse optional ALGORITHM ---
    raw_algo = data.get("ALGORITHM", "recursive_backtracker").lower()
    valid_algos = {"recursive_backtracker", "prim"}
    if raw_algo not in valid_algos:
        print(
            f"Error: unsupported ALGORITHM '{raw_algo}'. "
            f"Valid options: {valid_algos}"
        )
        sys.exit(1)

    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit_=exit_,
        output_file=data["OUTPUT_FILE"],
        perfect=perfect,
        seed=seed,
        algorithm=raw_algo,
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 config_parser.py <config_file>")
        sys.exit(1)

    config = parse_config(sys.argv[1])
    for attr, value in vars(config).items():
        print(f"{attr}: {value}")
