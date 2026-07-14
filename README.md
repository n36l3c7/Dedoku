# Dedoku

[![PyPI](https://img.shields.io/pypi/v/dedoku?color=2a78d6)](https://pypi.org/project/dedoku/)
[![Python versions](https://img.shields.io/pypi/pyversions/dedoku?logo=python&logoColor=white)](https://pypi.org/project/dedoku/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)](pyproject.toml)
[![Tests](https://github.com/n36l3c7/dedoku/actions/workflows/tests.yml/badge.svg)](https://github.com/n36l3c7/dedoku/actions/workflows/tests.yml)
[![Backtracking](https://img.shields.io/badge/backtracking-never-red)](#solving-philosophy)

A **pure-Python** Sudoku solving library that relies exclusively on
**human-style logical deduction** — 20 named technique families, from naked
singles to alternating inference chains, and not a single guess.

## About the project

Most Sudoku solvers brute-force the board: try a digit, propagate, undo on
contradiction. This library takes the opposite stance. Every digit placed and
every candidate eliminated is the conclusion of a **named, explainable
technique**, applied exactly the way a strong human solver would reason. The
full solving path is recorded step by step, so any solution can be replayed
and audited.

- **Zero external dependencies** — Python 3.10+ standard library only, tests
  included (`unittest`).
- **Fully typed and documented** — modern type hints and Sphinx-style
  reStructuredText docstrings on every module, class, and method.
- **Explainable solving** — each `Step` reports the technique, a
  human-readable description, the placements, and the eliminations.
- **Honestly benchmarked** — a reproducible 500-puzzle benchmark against a
  reference backtracking solver ships with the repo ([below](#benchmark)).

### Solving philosophy

**No backtracking. No guessing. Ever.** If the pipeline of logical techniques
cannot finish a puzzle, the solver stops and says so — it never falls back to
trial and error. On the benchmark's hardest tier this happens on 11 puzzles
out of 100; everything below that tier is solved outright.

## Installation

```bash
pip install dedoku
```

Or from source:

```bash
git clone https://github.com/n36l3c7/dedoku.git
cd dedoku
pip install -e .
```

Either way, no dependencies come with it — the package is pure standard
library.

## Usage

```python
from dedoku import Grid, SudokuSolver

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

print(result.solved)          # True
print(grid)                   # pretty-printed solved board
print(grid.to_string())       # 81-character string

for step in result.steps:     # the full, explainable solving path
    print(f"[{step.technique}] {step.description}")
print(result.techniques_used) # distinct techniques, in first-use order
```

Puzzle strings are 81 characters, read left to right, top to bottom: digits
`1`–`9` are givens, `0` or `.` mark empty cells; whitespace and the decoration
characters `|`, `-`, `+` are ignored, so pretty-printed boards parse back.

Need a custom pipeline? Pass any sequence of techniques, tried in order:

```python
from dedoku import SudokuSolver
from dedoku.techniques import HiddenSingle, NakedSingle, XYChain

solver = SudokuSolver(techniques=[NakedSingle(), HiddenSingle(), XYChain()])
```

The board model is fully navigable if you want to build your own techniques:
each `Cell` knows its `row`, `column`, `subgrid`, `candidates`, and `peers`;
the `Grid` exposes all 27 houses via `rows`, `columns`, `subgrids`, `units`.

## Implemented techniques

The default pipeline applies 28 technique instances from 20 families, always
restarting from the simplest after every deduction.

| # | Family | Classes | Module |
|---|--------|---------|--------|
| 1 | Naked Candidates | `NakedSingle`, `NakedPair`, `NakedTriple`, `NakedQuad` | [naked.py](dedoku/techniques/naked.py) |
| 2 | Hidden Candidates | `HiddenSingle`, `HiddenPair`, `HiddenTriple`, `HiddenQuad` | [hidden.py](dedoku/techniques/hidden.py) |
| 3 | Intersection Removal | `PointingCandidates`, `ClaimingCandidates` | [intersections.py](dedoku/techniques/intersections.py) |
| 4 | X-Wing | `XWing` | [fish.py](dedoku/techniques/fish.py) |
| 5 | Chute Remote Pairs | `ChuteRemotePairs` | [chute.py](dedoku/techniques/chute.py) |
| 6 | Simple Colouring | `SimpleColouring` | [colouring.py](dedoku/techniques/colouring.py) |
| 7 | W-Wing | `WWing` | [wwing.py](dedoku/techniques/wwing.py) |
| 8 | Y-Wing (XY-Wing) | `YWing` | [wings.py](dedoku/techniques/wings.py) |
| 9 | Unique Rectangles | `UniqueRectangle` (Type 1) | [rectangles.py](dedoku/techniques/rectangles.py) |
| 10 | Swordfish | `Swordfish` | [fish.py](dedoku/techniques/fish.py) |
| 11 | XYZ-Wing | `XYZWing` | [wings.py](dedoku/techniques/wings.py) |
| 12 | BUG (Bivalue Universal Grave) | `BivalueUniversalGrave` | [bug.py](dedoku/techniques/bug.py) |
| 13 | Avoidable Rectangles | `AvoidableRectangle` | [rectangles.py](dedoku/techniques/rectangles.py) |
| 14 | Unique Rectangles Type 2 | `UniqueRectangleType2` | [rectangles.py](dedoku/techniques/rectangles.py) |
| 15 | Finned Fish | `FinnedXWing`, `FinnedSwordfish` | [fish.py](dedoku/techniques/fish.py) |
| 16 | X-Chain (basic X-Cycles) | `XChain` | [chains.py](dedoku/techniques/chains.py) |
| 17 | XY-Chain | `XYChain` | [chains.py](dedoku/techniques/chains.py) |
| 18 | 3D Medusa | `Medusa3D` | [medusa.py](dedoku/techniques/medusa.py) |
| 19 | ALS-XZ (Almost Locked Sets) | `AlsXz` | [als.py](dedoku/techniques/als.py) |
| 20 | AIC (Alternating Inference Chains) | `AIC` | [aic.py](dedoku/techniques/aic.py) |

Uniqueness-based techniques (9, 12, 13, 14) assume the puzzle has exactly one
solution — the standard convention for published Sudokus.

## Benchmark

500 unique-solution puzzles (seed 42), 100 for each of five difficulty
levels, timed against the **lightest classic backtracking solver** (bitmask,
sequential cells, no heuristics). Same protocol for both solvers: puzzle
string in, board out, minimum of 3 runs, parsing included. Python 3.13,
Windows 11. Levels are graded by the hardest technique the original
13-family pipeline needs: singles → subsets → intersections → advanced →
*extreme* (beyond that base pipeline).

### Solve-time distribution

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/n36l3c7/dedoku/main/docs/benchmark-distribution-dark.svg">
  <img alt="Solve-time distribution by difficulty level: one dot per puzzle on a logarithmic ms scale, backtracking vs logic library, with medians marked" src="https://raw.githubusercontent.com/n36l3c7/dedoku/main/docs/benchmark-distribution-light.svg">
</picture>

| Level | Solved by library | BT median | BT p95 | BT max | Library median | Library p95 | Library max |
|---|---|---|---|---|---|---|---|
| 1 · Singles | 100/100 | 15.9 ms | 481 ms | 1,757 ms | **1.1 ms** | 1.6 ms | 1.8 ms |
| 2 · Subsets | 100/100 | 13.1 ms | 218 ms | 2,172 ms | **1.6 ms** | 2.4 ms | 2.9 ms |
| 3 · Intersections | 100/100 | 5.0 ms | 126 ms | 2,026 ms | **3.1 ms** | 7.8 ms | 12.1 ms |
| 4 · Advanced | 100/100 | 15.6 ms | 225 ms | 551 ms | **7.5 ms** | 17.7 ms | 31.2 ms |
| 5 · Extreme | 89/100 † | **16.7 ms** | 229 ms | 684 ms | 65.4 ms | 306 ms | 720 ms |
| **Overall** | **489/500** | 12.6 ms | 279 ms | 2,172 ms | **3.0 ms** | 158 ms | 720 ms |

† On the 11 extreme puzzles the library cannot crack, its reported time is
the time to exhaust every technique and stop — never a guess.

Key findings:

- **The logic library wins on the median at every human-graded level up to
  Advanced** (3.0 ms vs 12.6 ms overall) and is far more predictable: naive
  backtracking's worst case is 2.2 s when the cell order is unlucky, versus
  0.72 s for the library's hardest chain solve.
- **Brute-force time is uncorrelated with human difficulty** — backtracking
  is fastest on level 3 and slowest on level 1, while the library's times
  grow monotonically with the level. The two solvers measure different
  notions of "hard".
- **Level 5 is chain territory**: the advanced techniques added in v0.2.0
  raised the library's extreme-tier solve rate from 0/100 to 89/100.

### Which techniques crack the extreme tier

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/n36l3c7/dedoku/main/docs/benchmark-techniques-dark.svg">
  <img alt="Number of solved extreme puzzles in which each advanced technique fired, XY-Chain leading with 55 of 89" src="https://raw.githubusercontent.com/n36l3c7/dedoku/main/docs/benchmark-techniques-light.svg">
</picture>

### Reproduce it

```bash
python benchmark/generate_puzzles.py   # optional: regenerate the dataset (seeded)
python benchmark/run_benchmark.py      # times both solvers, writes benchmark/results.csv
python benchmark/make_charts.py        # renders the SVG charts into docs/
```

## Architecture

| Class | Responsibility |
|-------|----------------|
| `Cell` | A single cell: value, candidates, position, given flag, and references to its row, column, and subgrid. |
| `Unit` → `Row`, `Column`, `Subgrid` | The 27 houses of nine cells, sharing bookkeeping logic. |
| `Grid` | The full 9×9 board: wiring, parsing, serialisation, validity. |
| `Technique` / `Step` | One logical strategy and the immutable record of one applied deduction. |
| `SudokuSolver` / `SolveResult` | The engine that chains techniques and the outcome of a session. |

## Development

```bash
python -m unittest discover -s tests -v   # 79 tests, includes the step oracle
python -m ruff check dedoku tests benchmark
python -m mypy dedoku
python -m coverage run -m unittest discover -s tests && python -m coverage report
```

CI runs the suite on Linux, Windows, and macOS across Python 3.10–3.14,
with ruff, mypy, and a 95% coverage gate. Beyond unit tests, an *oracle*
check verifies that every placement matches an independent backtracking
solution and that no elimination ever removes a true digit — the
library's core contract, tested directly.

### Soundness validation

```bash
python benchmark/validate.py --count 5000 --seed 7
```

Latest run: **5,000 generated puzzles, every single deduction verified —
4,933 solved, 67 stalled (extreme chain territory), 0 unsound steps.**

## License

Released under the [MIT License](LICENSE).
