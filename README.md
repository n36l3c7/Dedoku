# Sudoku-Solver

A **pure-Python** Sudoku solving library that relies exclusively on **human-style
logical deduction techniques**.

## Philosophy

**No backtracking. No guessing. Ever.**

Every digit placed and every candidate eliminated is the result of a named,
explainable logical technique — exactly the way a human expert solves a puzzle.
The solver applies its techniques in a loop, from the simplest to the most
advanced, and records each step so the full solving path can be inspected and
explained.

## Features

- **Zero external dependencies** — Python standard library only (Python 3.10+).
- **Fully typed** — modern type hints throughout the code base.
- **Fully documented** — Sphinx-style reStructuredText docstrings on every
  module, class, and method.
- **Explainable solving** — every step reports the technique used, the
  placements made, and the candidates eliminated.

## Architecture

The board is modelled with a small object-oriented hierarchy:

| Class     | Responsibility                                                        |
| --------- | --------------------------------------------------------------------- |
| `Cell`    | A single cell: value, candidates, position, and references to its row, column, and subgrid. |
| `Unit`    | Abstract base for any house of nine cells (shared logic).             |
| `Row`     | A horizontal line of nine cells.                                      |
| `Column`  | A vertical line of nine cells.                                        |
| `Subgrid` | A 3×3 box of nine cells.                                              |
| `Grid`    | The full 9×9 board wiring cells, rows, columns, and subgrids together. |

The solving engine lives on top of the board model:

| Class          | Responsibility                                             |
| -------------- | ---------------------------------------------------------- |
| `Technique`    | Abstract base class for a single logical strategy.         |
| `Step`         | Immutable record of one applied step (placements/eliminations). |
| `SudokuSolver` | Applies the techniques in order until solved or stuck.     |
| `SolveResult`  | Outcome of a solving session: status and full step list.   |

## Technique roadmap

Implemented step by step, from simplest to most advanced:

1. [x] **Naked Candidates** (Single, Pair, Triple, Quad)
2. [x] **Hidden Candidates** (Single, Pair, Triple, Quad)
3. [x] **Intersection Removal** (Pointing and Claiming)
4. [x] **X-Wing**
5. [x] **Chute Remote Pairs**
6. [ ] **Simple Colouring**
7. [ ] **W-Wing**
8. [ ] **Y-Wing** (XY-Wing)
9. [ ] **Rectangle Elimination** (Unique Rectangles)
10. [ ] **Swordfish**
11. [ ] **XYZ-Wing**
12. [ ] **BUG** (Bivalue Universal Grave)
13. [ ] **Avoidable Rectangles**

## Usage

```python
from sudoku_solver import Grid, SudokuSolver

puzzle = (
    "530070000"
    "600195000"
    "098000060"
    "800060003"
    "400803001"
    "700020006"
    "060000280"
    "000419005"
    "000080079"
)

grid = Grid.from_string(puzzle)
result = SudokuSolver().solve(grid)

print(grid)                      # pretty-printed board
print(result.solved)             # True
for step in result.steps:        # full, explainable solving path
    print(f"[{step.technique}] {step.description}")
```

Puzzle strings are 81 characters long, read left to right, top to bottom.
Digits `1`–`9` are givens; `0` or `.` mark empty cells. Whitespace and the
decoration characters `|`, `-`, `+` are ignored, so pretty-printed boards can
be parsed back.

## Development

Run the test suite (standard library `unittest`, no extra tooling required):

```bash
python -m unittest discover -s tests -v
```

Install the package in editable mode:

```bash
pip install -e .
```
