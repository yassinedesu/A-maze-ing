PY = python3
SRC = a_maze_ing.py
CONFIG = config.txt

install:
	$(PY) -m pip install -r requirements.txt

run:
	$(PY) $(SRC) $(CONFIG)

debug:
	$(PY) -m pdb $(SRC) $(CONFIG)

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null; true

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
	--disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

.PHONY: install run debug clean lint lint-strict