"""Cell model for the Sudoku board.

This module defines :class:`Cell`, the smallest building block of a Sudoku
grid. A cell knows its position, its solved value (if any), its remaining
candidate digits, and holds references to the three houses it belongs to:
its :class:`~sudoku_solver.units.Row`, :class:`~sudoku_solver.units.Column`,
and :class:`~sudoku_solver.units.Subgrid`.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .exceptions import ContradictionError

if TYPE_CHECKING:
    from .units import Column, Row, Subgrid

__all__ = ["DIGITS", "Cell"]

DIGITS: frozenset[int] = frozenset(range(1, 10))
"""frozenset[int]: The nine digits a Sudoku cell may contain."""


class Cell:
    """A single cell of a 9x9 Sudoku grid.

    A cell starts unsolved with all nine digits as candidates. Placing a
    value with :meth:`set_value` automatically removes that digit from the
    candidates of every peer (the cells sharing a row, column, or subgrid).

    :param row_index: Zero-based index of the row the cell lies in (0-8).
    :type row_index: int
    :param column_index: Zero-based index of the column the cell lies in (0-8).
    :type column_index: int
    :raises ValueError: If either index is outside the 0-8 range.
    """

    __slots__ = ("_row_index", "_column_index", "_value", "_candidates",
                 "_row", "_column", "_subgrid", "_is_given",
                 "_peers_cache", "_candidates_view")

    def __init__(self, row_index: int, column_index: int) -> None:
        if row_index not in range(9) or column_index not in range(9):
            raise ValueError(
                f"cell position must be within 0-8, "
                f"got ({row_index}, {column_index})"
            )
        self._row_index = row_index
        self._column_index = column_index
        self._value: int | None = None
        self._candidates: set[int] = set(DIGITS)
        self._row: Row | None = None
        self._column: Column | None = None
        self._subgrid: Subgrid | None = None
        self._is_given = False
        self._peers_cache: tuple[Cell, ...] | None = None
        self._candidates_view: frozenset[int] | None = None

    # ------------------------------------------------------------------
    # Wiring
    # ------------------------------------------------------------------
    def attach(self, row: Row, column: Column, subgrid: Subgrid) -> None:
        """Wire the cell to its three houses and register it with each.

        This is called once by :class:`~sudoku_solver.grid.Grid` while the
        board is being built and must not be called again afterwards.

        :param row: The row the cell belongs to.
        :type row: Row
        :param column: The column the cell belongs to.
        :type column: Column
        :param subgrid: The 3x3 subgrid the cell belongs to.
        :type subgrid: Subgrid
        :raises RuntimeError: If the cell is already attached.
        """
        if self._row is not None:
            raise RuntimeError(f"cell {self.label} is already attached")
        self._row = row
        self._column = column
        self._subgrid = subgrid
        for unit in (row, column, subgrid):
            unit.register(self)

    # ------------------------------------------------------------------
    # Read-only state
    # ------------------------------------------------------------------
    @property
    def row_index(self) -> int:
        """int: Zero-based index of the cell's row."""
        return self._row_index

    @property
    def column_index(self) -> int:
        """int: Zero-based index of the cell's column."""
        return self._column_index

    @property
    def position(self) -> tuple[int, int]:
        """tuple[int, int]: The ``(row_index, column_index)`` pair."""
        return (self._row_index, self._column_index)

    @property
    def label(self) -> str:
        """str: Human-readable, one-based position label such as ``R4C7``."""
        return f"R{self._row_index + 1}C{self._column_index + 1}"

    @property
    def row(self) -> Row:
        """Row: The row the cell belongs to.

        :raises RuntimeError: If the cell has not been attached to a grid.
        """
        if self._row is None:
            raise RuntimeError(f"cell {self.label} is not attached to a grid")
        return self._row

    @property
    def column(self) -> Column:
        """Column: The column the cell belongs to.

        :raises RuntimeError: If the cell has not been attached to a grid.
        """
        if self._column is None:
            raise RuntimeError(f"cell {self.label} is not attached to a grid")
        return self._column

    @property
    def subgrid(self) -> Subgrid:
        """Subgrid: The 3x3 subgrid the cell belongs to.

        :raises RuntimeError: If the cell has not been attached to a grid.
        """
        if self._subgrid is None:
            raise RuntimeError(f"cell {self.label} is not attached to a grid")
        return self._subgrid

    @property
    def value(self) -> int | None:
        """int | None: The solved digit, or ``None`` while unsolved."""
        return self._value

    @property
    def candidates(self) -> frozenset[int]:
        """frozenset[int]: Immutable view of the remaining candidates.

        A solved cell exposes an empty set. The view is cached between
        mutations, so repeated reads are cheap.
        """
        if self._candidates_view is None:
            self._candidates_view = frozenset(self._candidates)
        return self._candidates_view

    @property
    def is_solved(self) -> bool:
        """bool: Whether the cell holds a definitive value."""
        return self._value is not None

    @property
    def is_given(self) -> bool:
        """bool: Whether the value was part of the original puzzle.

        Uniqueness-based techniques (such as avoidable rectangles) must
        distinguish clues supplied by the puzzle from values deduced
        during solving.
        """
        return self._is_given

    @property
    def is_bivalue(self) -> bool:
        """bool: Whether the cell is unsolved with exactly two candidates.

        Bivalue cells are the anchors of several advanced techniques
        (remote pairs, W-Wing, Y-Wing, BUG, ...).
        """
        return self._value is None and len(self._candidates) == 2

    @property
    def peers(self) -> tuple[Cell, ...]:
        """tuple[Cell, ...]: The 20 distinct cells sharing a house with this one.

        Peers are returned sorted by position for deterministic iteration
        and cached after the first access, since the wiring never changes.

        :raises RuntimeError: If the cell has not been attached to a grid.
        """
        if self._peers_cache is None:
            seen: dict[int, Cell] = {}
            for unit in (self.row, self.column, self.subgrid):
                for cell in unit.cells:
                    if cell is not self:
                        seen[id(cell)] = cell
            self._peers_cache = tuple(
                sorted(seen.values(), key=lambda cell: cell.position)
            )
        return self._peers_cache

    def sees(self, other: Cell) -> bool:
        """Report whether ``other`` shares a house with this cell.

        A cell never sees itself.

        :param other: The cell to test against.
        :type other: Cell
        :returns: ``True`` if the two cells share a row, column, or
            subgrid.
        :rtype: bool
        """
        return other is not self and (
            self._row_index == other.row_index
            or self._column_index == other.column_index
            or self.subgrid.index == other.subgrid.index
        )

    # ------------------------------------------------------------------
    # Mutation
    # ------------------------------------------------------------------
    def set_value(self, digit: int) -> None:
        """Solve the cell with ``digit`` and propagate to all peers.

        The digit is removed from the candidates of every peer, which may
        in turn reveal a contradiction elsewhere on the board.

        :param digit: The digit to place, between 1 and 9.
        :type digit: int
        :raises ValueError: If ``digit`` is not a digit between 1 and 9,
            or the cell is already solved.
        :raises ContradictionError: If ``digit`` is not among the cell's
            candidates, or placing it strips the last candidate from an
            unsolved peer.
        """
        _validate_digit(digit)
        if self._value is not None:
            raise ValueError(
                f"cell {self.label} is already solved with {self._value}"
            )
        if digit not in self._candidates:
            raise ContradictionError(
                f"digit {digit} is not a candidate of cell {self.label}"
            )
        self._value = digit
        self._candidates.clear()
        self._candidates_view = None
        for peer in self.peers:
            peer.remove_candidate(digit)

    def mark_as_given(self) -> None:
        """Flag the cell's value as an original clue of the puzzle.

        This is called by :meth:`sudoku_solver.grid.Grid.from_string`
        right after each given is placed.

        :raises ValueError: If the cell has no value yet.
        """
        if self._value is None:
            raise ValueError(
                f"cell {self.label} is unsolved and cannot be a given"
            )
        self._is_given = True

    def remove_candidate(self, digit: int) -> bool:
        """Eliminate ``digit`` from the cell's candidates.

        Removing a candidate from a solved cell, or a digit that is already
        absent, is a harmless no-op.

        :param digit: The digit to eliminate, between 1 and 9.
        :type digit: int
        :returns: ``True`` if the candidate was present and got removed.
        :rtype: bool
        :raises ValueError: If ``digit`` is not a digit between 1 and 9.
        :raises ContradictionError: If the removal leaves an unsolved cell
            with no candidates at all.
        """
        _validate_digit(digit)
        if self._value is not None or digit not in self._candidates:
            return False
        self._candidates.discard(digit)
        self._candidates_view = None
        if not self._candidates:
            raise ContradictionError(
                f"cell {self.label} has no candidates left"
            )
        return True

    def __repr__(self) -> str:
        """Return a debugging representation of the cell.

        :returns: A string such as ``<Cell R1C1 value=5>`` or
            ``<Cell R1C2 candidates={1, 2}>``.
        :rtype: str
        """
        if self._value is not None:
            return f"<Cell {self.label} value={self._value}>"
        return f"<Cell {self.label} candidates={sorted(self._candidates)}>"


def _validate_digit(digit: int) -> None:
    """Ensure ``digit`` is an integer between 1 and 9.

    :param digit: The value to validate.
    :type digit: int
    :raises ValueError: If ``digit`` is not a valid Sudoku digit.
    """
    if not isinstance(digit, int) or digit not in DIGITS:
        raise ValueError(f"digit must be an integer between 1 and 9, got {digit!r}")
