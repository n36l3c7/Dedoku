"""A pure-Python Sudoku solver based on human-style logical deduction.

The package exposes an object-oriented board model (:class:`Cell`,
:class:`Row`, :class:`Column`, :class:`Subgrid`, :class:`Grid`) and a
logic-only solving engine (:class:`SudokuSolver`) that never resorts to
backtracking. It has no external dependencies.

Individual techniques live in :mod:`dedoku.techniques`.
"""

from __future__ import annotations

from .cell import DIGITS, Cell
from .exceptions import ContradictionError, InvalidGridError, SudokuError
from .grid import Grid
from .solver import SolveResult, SudokuSolver
from .techniques import Elimination, Placement, Step, Technique
from .units import Column, Row, Subgrid, Unit

__version__ = "0.6.0"

__all__ = [
    "DIGITS",
    "Cell",
    "Column",
    "ContradictionError",
    "Elimination",
    "Grid",
    "InvalidGridError",
    "Placement",
    "Row",
    "SolveResult",
    "Step",
    "Subgrid",
    "SudokuError",
    "SudokuSolver",
    "Technique",
    "Unit",
    "__version__",
    "solve",
]


def solve(
    puzzle: str,
    *,
    method: str = "logic",
    assume_unique: bool = True,
) -> SolveResult:
    """Solve a puzzle string in one call.

    Convenience wrapper around :class:`Grid` and :class:`SudokuSolver`:
    parses the 81-character puzzle, solves it with the chosen method,
    and returns the outcome with the final board in ``result.grid``.

    :param puzzle: The puzzle description accepted by
        :meth:`Grid.from_string`.
    :type puzzle: str
    :param method: How to solve. ``"logic"`` (default) uses the
        explainable techniques only and may stall on the hardest
        puzzles; ``"hybrid"`` runs the techniques first and completes
        any remainder by brute force; ``"backtracking"`` skips the
        techniques and brute-forces directly. Non-default methods
        record their brute-force part as an explicit ``"Backtracking"``
        step (see ``result.used_backtracking``).
    :type method: str
    :param assume_unique: When ``False``, uniqueness-based techniques are
        excluded, keeping every deduction sound even if the puzzle might
        have multiple solutions. Recommended together with ``"hybrid"``
        when the puzzle is not guaranteed to have one solution.
    :type assume_unique: bool
    :returns: The session outcome; ``result.grid`` holds the final board
        and ``result.steps`` the full explainable solving path.
    :rtype: SolveResult
    :raises ValueError: If ``method`` is not one of the three modes.
    :raises InvalidGridError: If the puzzle description is malformed or
        its givens contradict each other.
    :raises ContradictionError: If the puzzle has no solution (detected
        by logic, or proven exhaustively by the non-default methods).
    """
    grid = Grid.from_string(puzzle)
    if method == "logic":
        solver = SudokuSolver(assume_unique=assume_unique)
    elif method == "hybrid":
        solver = SudokuSolver(
            assume_unique=assume_unique, backtracking_fallback=True
        )
    elif method == "backtracking":
        solver = SudokuSolver(techniques=(), backtracking_fallback=True)
    else:
        raise ValueError(
            f"method must be 'logic', 'hybrid', or 'backtracking', "
            f"got {method!r}"
        )
    return solver.solve(grid)
