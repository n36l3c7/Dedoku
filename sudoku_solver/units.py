"""House models: rows, columns, and subgrids.

A *house* (called a *unit* in this library) is any group of nine cells that
must contain each digit exactly once. The shared behaviour lives in
:class:`Unit`; :class:`Row`, :class:`Column`, and :class:`Subgrid` are thin
subclasses that mostly provide a human-readable identity.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Iterator

from .cell import DIGITS

if TYPE_CHECKING:
    from .cell import Cell

__all__ = ["Unit", "Row", "Column", "Subgrid"]


class Unit:
    """Base class for any house of nine cells.

    :param index: Zero-based index of the unit within its kind (0-8).
    :type index: int
    :raises ValueError: If ``index`` is outside the 0-8 range.

    :cvar kind: Lower-case human-readable name of the unit kind
        (``"row"``, ``"column"``, or ``"subgrid"``).
    """

    kind: str = "unit"

    def __init__(self, index: int) -> None:
        if index not in range(9):
            raise ValueError(f"unit index must be within 0-8, got {index}")
        self._index = index
        self._cells: list[Cell] = []
        self._cells_view: tuple[Cell, ...] | None = None

    def register(self, cell: Cell) -> None:
        """Add ``cell`` to the unit while the grid is being built.

        This is called by :meth:`sudoku_solver.cell.Cell.attach` and must
        not be used afterwards.

        :param cell: The cell to register.
        :type cell: Cell
        :raises RuntimeError: If the unit already holds nine cells.
        """
        if len(self._cells) >= 9:
            raise RuntimeError(f"{self.name} already holds nine cells")
        self._cells.append(cell)
        self._cells_view = None

    # ------------------------------------------------------------------
    # Identity
    # ------------------------------------------------------------------
    @property
    def index(self) -> int:
        """int: Zero-based index of the unit within its kind."""
        return self._index

    @property
    def name(self) -> str:
        """str: Human-readable, one-based name such as ``row 3``."""
        return f"{self.kind} {self._index + 1}"

    # ------------------------------------------------------------------
    # Cell access
    # ------------------------------------------------------------------
    @property
    def cells(self) -> tuple[Cell, ...]:
        """tuple[Cell, ...]: The nine cells of the unit, in board order.

        The tuple is cached, since the wiring never changes once built.
        """
        if self._cells_view is None:
            self._cells_view = tuple(self._cells)
        return self._cells_view

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over the cells of the unit in board order.

        :returns: An iterator over the unit's cells.
        :rtype: Iterator[Cell]
        """
        return iter(self._cells)

    def __len__(self) -> int:
        """Return the number of registered cells.

        :returns: The cell count (nine once the grid is fully built).
        :rtype: int
        """
        return len(self._cells)

    def __getitem__(self, position: int) -> Cell:
        """Return the cell at ``position`` within the unit.

        :param position: Zero-based position inside the unit.
        :type position: int
        :returns: The requested cell.
        :rtype: Cell
        """
        return self._cells[position]

    # ------------------------------------------------------------------
    # Digit bookkeeping
    # ------------------------------------------------------------------
    def solved_values(self) -> frozenset[int]:
        """Return the digits already placed inside the unit.

        :returns: The set of solved digits.
        :rtype: frozenset[int]
        """
        return frozenset(
            cell.value for cell in self._cells if cell.value is not None
        )

    def missing_values(self) -> frozenset[int]:
        """Return the digits still to be placed inside the unit.

        :returns: The complement of :meth:`solved_values`.
        :rtype: frozenset[int]
        """
        return DIGITS - self.solved_values()

    def unsolved_cells(self) -> tuple[Cell, ...]:
        """Return the cells of the unit that have no value yet.

        :returns: The unsolved cells, in board order.
        :rtype: tuple[Cell, ...]
        """
        return tuple(cell for cell in self._cells if not cell.is_solved)

    def cells_with_candidate(self, digit: int) -> tuple[Cell, ...]:
        """Return the unsolved cells that still allow ``digit``.

        :param digit: The digit to look for, between 1 and 9.
        :type digit: int
        :returns: The matching cells, in board order.
        :rtype: tuple[Cell, ...]
        """
        return tuple(
            cell for cell in self._cells if digit in cell.candidates
        )

    def is_valid(self) -> bool:
        """Check that no digit appears twice among the solved cells.

        :returns: ``True`` if every solved digit is unique in the unit.
        :rtype: bool
        """
        values = [cell.value for cell in self._cells if cell.value is not None]
        return len(values) == len(set(values))

    def __repr__(self) -> str:
        """Return a debugging representation of the unit.

        :returns: A string such as ``<Row 3>``.
        :rtype: str
        """
        return f"<{type(self).__name__} {self._index + 1}>"


class Row(Unit):
    """A horizontal line of nine cells."""

    kind = "row"


class Column(Unit):
    """A vertical line of nine cells."""

    kind = "column"


class Subgrid(Unit):
    """A 3x3 box of nine cells.

    Subgrids are indexed left to right, top to bottom: subgrid 0 covers
    rows 0-2 and columns 0-2, subgrid 8 covers rows 6-8 and columns 6-8.
    """

    kind = "subgrid"
