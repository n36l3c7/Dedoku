"""Exception hierarchy for the :mod:`sudoku_solver` package.

All exceptions raised by this library derive from :class:`SudokuError`,
so callers can catch a single base class to handle any library failure.
"""

from __future__ import annotations

__all__ = ["SudokuError", "InvalidGridError", "ContradictionError"]


class SudokuError(Exception):
    """Base class for every exception raised by :mod:`sudoku_solver`."""


class InvalidGridError(SudokuError):
    """Raised when a puzzle description cannot be turned into a valid grid.

    Typical causes are a wrong number of cells, characters outside the
    accepted alphabet, or givens that immediately contradict each other
    (for example two identical digits in the same row).
    """


class ContradictionError(SudokuError):
    """Raised when the board reaches a logically impossible state.

    This happens when an unsolved cell loses its last candidate or a digit
    has no remaining home inside a unit. During solving it means the puzzle
    (or the technique that produced the state) is inconsistent.
    """
