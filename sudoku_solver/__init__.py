"""A pure-Python Sudoku solver based on human-style logical deduction.

The package exposes an object-oriented board model (:class:`Cell`,
:class:`Row`, :class:`Column`, :class:`Subgrid`, :class:`Grid`) with no
external dependencies.
"""

from __future__ import annotations

from .cell import DIGITS, Cell
from .exceptions import ContradictionError, InvalidGridError, SudokuError
from .grid import Grid
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
    "Subgrid",
    "SudokuError",
    "Unit",
    "__version__",
]
