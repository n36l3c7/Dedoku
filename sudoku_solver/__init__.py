"""A pure-Python Sudoku solver based on human-style logical deduction.

The package exposes an object-oriented board model (:class:`Cell`,
:class:`Row`, :class:`Column`, :class:`Subgrid`, :class:`Grid`) and a
logic-only solving engine (:class:`SudokuSolver`) that never resorts to
backtracking. It has no external dependencies.

Individual techniques live in :mod:`sudoku_solver.techniques`.
"""

from __future__ import annotations

from .cell import DIGITS, Cell
from .exceptions import ContradictionError, InvalidGridError, SudokuError
from .grid import Grid
from .solver import SolveResult, SudokuSolver
from .techniques import Step, Technique
from .units import Column, Row, Subgrid, Unit

__version__ = "0.1.0"

__all__ = [
    "DIGITS",
    "Cell",
    "Column",
    "ContradictionError",
    "Grid",
    "InvalidGridError",
    "Row",
    "SolveResult",
    "Step",
    "Subgrid",
    "SudokuError",
    "SudokuSolver",
    "Technique",
    "Unit",
    "__version__",
]
