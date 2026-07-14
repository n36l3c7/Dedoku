# Changelog

All notable changes to this project are documented in this file.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project adheres to [Semantic Versioning](https://semver.org/).

## [0.7.0] - 2026-07-14

### Added
- Opt-in brute force. `dedoku.solve(puzzle, method=...)` accepts
  `"logic"` (default, unchanged), `"hybrid"` (logical techniques first,
  depth-first search completes any remainder), and `"backtracking"`
  (search directly); the CLI gains `--method` and
  `SudokuSolver(backtracking_fallback=True)` exposes the same at class
  level. The search honours the current candidates, and anything
  brute-forced is recorded as an explicit `"Backtracking"` step —
  `SolveResult.used_backtracking` reports whether it ran.

### Changed
- Nothing in the default behaviour: logic only, never guessing, exactly
  as before.

## [0.6.0] - 2026-07-14

### Added
- Command-line interface: `dedoku` (also `python -m dedoku`) solves a
  puzzle from the argument or stdin; `--explain` prints every deduction
  in order, showing how each cell was filled; `--multi` disables
  uniqueness-based techniques. Exit codes: 0 solved, 1 stalled,
  2 invalid input.
- Documentation site at <https://n36l3c7.github.io/dedoku/> (Sphinx +
  furo), built from the RST docstrings and deployed from CI on every
  push: usage guide, CLI reference, per-family technique explanations,
  benchmark, and full API reference.

## [0.5.0] - 2026-07-14

API-freeze release on the road to 1.0.

### Added
- `dedoku.solve(puzzle, *, assume_unique=True)` — one-call solving that
  returns a `SolveResult` with the final board attached as `result.grid`.
- `SolveResult.grid` — the board a session worked on, solved or partial.
- `SudokuSolver(assume_unique=False)` and
  `Technique.requires_unique_solution` — exclude uniqueness-based
  techniques (unique rectangles, BUG, avoidable rectangles) so every
  deduction stays sound on puzzles that may have multiple solutions.
- `Placement` and `Elimination` NamedTuples: `Step.placements` and
  `Step.eliminations` entries now expose `row`, `column`, and `digit`
  fields while remaining fully compatible with the bare 3-tuples they
  replace (equality, unpacking, indexing).

## [0.4.0] - 2026-07-14

Quality and soundness release.

### Added
- `py.typed` marker: downstream type checkers now consume the inline
  annotations.
- Step-level oracle tests: every placement is checked against an
  independent backtracking solution and no elimination may ever remove a
  true digit.
- `benchmark/validate.py`: reproducible mass validation (latest run:
  5,000 puzzles, 4,933 solved, 67 stalled, 0 unsound deductions).
- Cross-platform CI: Linux/Windows/macOS x Python 3.10-3.14, with ruff,
  mypy, and a 95% coverage gate.

## [0.3.0] - 2026-07-14

First release published to PyPI.

### Changed
- **Breaking:** project, distribution, and import package renamed from
  `sudoku-solver` / `sudoku_solver` to **`dedoku`**.
- Releases are published via GitHub Actions with PyPI trusted publishing
  on every `v*` tag.

## [0.2.0] - 2026-07-14

### Added
- Seven advanced technique families: Unique Rectangle Type 2, finned
  X-Wing/Swordfish, X-Chain, XY-Chain, 3D Medusa, ALS-XZ, and AIC —
  raising the extreme-tier solve rate from 0/100 to 89/100.
- Reproducible 500-puzzle benchmark suite against a reference
  backtracking solver, with theme-aware SVG charts.
- MIT license.

### Changed
- Roughly 4x faster solving through peer/candidate/unit caching.

## [0.1.0] - 2026-07-14

### Added
- Object-oriented board model (`Cell`, `Row`, `Column`, `Subgrid`,
  `Grid`) with candidate tracking and automatic propagation.
- Logic-only solving engine with the original 13 technique families,
  from naked singles to avoidable rectangles — no backtracking, ever.

[0.7.0]: https://github.com/n36l3c7/dedoku/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/n36l3c7/dedoku/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/n36l3c7/dedoku/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/n36l3c7/dedoku/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/n36l3c7/dedoku/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/n36l3c7/dedoku/compare/8a501f8...v0.2.0
[0.1.0]: https://github.com/n36l3c7/dedoku/commits/22c34c6
