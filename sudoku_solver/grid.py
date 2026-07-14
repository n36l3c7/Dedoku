"""The full 9x9 Sudoku board.

:class:`Grid` builds the 81 :class:`~sudoku_solver.cell.Cell` objects, wires
each of them to its :class:`~sudoku_solver.units.Row`,
:class:`~sudoku_solver.units.Column`, and
:class:`~sudoku_solver.units.Subgrid`, and offers parsing and serialisation
helpers.
"""

from __future__ import annotations

from typing import Iterator

from .cell import Cell
from .exceptions import ContradictionError, InvalidGridError
from .units import Column, Row, Subgrid, Unit

__all__ = ["Grid"]

_EMPTY_CHARS = ".0"
_IGNORED_CHARS = " \t\r\n|+-"


class Grid:
    """A 9x9 Sudoku board made of cells, rows, columns, and subgrids.

    A freshly constructed grid is empty: every cell is unsolved with all
    nine candidates. Use :meth:`from_string` to load a puzzle.
    """

    def __init__(self) -> None:
        self._rows: tuple[Row, ...] = tuple(Row(i) for i in range(9))
        self._columns: tuple[Column, ...] = tuple(Column(i) for i in range(9))
        self._subgrids: tuple[Subgrid, ...] = tuple(Subgrid(i) for i in range(9))
        cells: list[Cell] = []
        for row_index in range(9):
            for column_index in range(9):
                cell = Cell(row_index, column_index)
                cell.attach(
                    self._rows[row_index],
                    self._columns[column_index],
                    self._subgrids[self.subgrid_index(row_index, column_index)],
                )
                cells.append(cell)
        self._cells: tuple[Cell, ...] = tuple(cells)
        self._units: tuple[Unit, ...] = (
            self._rows + self._columns + self._subgrids
        )

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------
    @classmethod
    def from_string(cls, text: str) -> Grid:
        """Build a grid from an 81-character puzzle description.

        Cells are read left to right, top to bottom. Digits ``1``-``9``
        are givens, while ``0`` and ``.`` mark empty cells. Whitespace and
        the decoration characters ``|``, ``+``, ``-`` are ignored, so the
        output of :meth:`__str__` can be parsed back.

        :param text: The puzzle description.
        :type text: str
        :returns: A grid with all givens placed and candidates propagated.
        :rtype: Grid
        :raises InvalidGridError: If the description does not contain
            exactly 81 cells, uses unexpected characters, or its givens
            contradict each other.
        """
        symbols: list[str] = []
        for char in text:
            if char in _IGNORED_CHARS:
                continue
            if char.isdigit() or char in _EMPTY_CHARS:
                symbols.append(char)
            else:
                raise InvalidGridError(
                    f"unexpected character {char!r} in puzzle description"
                )
        if len(symbols) != 81:
            raise InvalidGridError(
                f"puzzle must describe 81 cells, got {len(symbols)}"
            )
        grid = cls()
        for position, symbol in enumerate(symbols):
            if symbol in _EMPTY_CHARS:
                continue
            try:
                grid._cells[position].set_value(int(symbol))
            except ContradictionError as exc:
                raise InvalidGridError(
                    f"the givens contradict each other: {exc}"
                ) from exc
            grid._cells[position].mark_as_given()
        return grid

    # ------------------------------------------------------------------
    # Geometry helpers
    # ------------------------------------------------------------------
    @staticmethod
    def subgrid_index(row_index: int, column_index: int) -> int:
        """Return the subgrid index covering the given board position.

        :param row_index: Zero-based row index (0-8).
        :type row_index: int
        :param column_index: Zero-based column index (0-8).
        :type column_index: int
        :returns: The zero-based subgrid index (0-8).
        :rtype: int
        """
        return (row_index // 3) * 3 + column_index // 3

    def cell(self, row_index: int, column_index: int) -> Cell:
        """Return the cell at the given board position.

        :param row_index: Zero-based row index (0-8).
        :type row_index: int
        :param column_index: Zero-based column index (0-8).
        :type column_index: int
        :returns: The requested cell.
        :rtype: Cell
        :raises ValueError: If either index is outside the 0-8 range.
        """
        if row_index not in range(9) or column_index not in range(9):
            raise ValueError(
                f"cell position must be within 0-8, "
                f"got ({row_index}, {column_index})"
            )
        return self._cells[row_index * 9 + column_index]

    # ------------------------------------------------------------------
    # Collections
    # ------------------------------------------------------------------
    @property
    def cells(self) -> tuple[Cell, ...]:
        """tuple[Cell, ...]: All 81 cells, left to right, top to bottom."""
        return self._cells

    @property
    def rows(self) -> tuple[Row, ...]:
        """tuple[Row, ...]: The nine rows, top to bottom."""
        return self._rows

    @property
    def columns(self) -> tuple[Column, ...]:
        """tuple[Column, ...]: The nine columns, left to right."""
        return self._columns

    @property
    def subgrids(self) -> tuple[Subgrid, ...]:
        """tuple[Subgrid, ...]: The nine subgrids, left to right, top to bottom."""
        return self._subgrids

    @property
    def units(self) -> tuple[Unit, ...]:
        """tuple[Unit, ...]: All 27 houses: rows, then columns, then subgrids."""
        return self._units

    def __iter__(self) -> Iterator[Cell]:
        """Iterate over all 81 cells in board order.

        :returns: An iterator over the grid's cells.
        :rtype: Iterator[Cell]
        """
        return iter(self._cells)

    # ------------------------------------------------------------------
    # Board state
    # ------------------------------------------------------------------
    def is_solved(self) -> bool:
        """Check whether every cell holds a value and the board is valid.

        :returns: ``True`` if the puzzle is completely and correctly solved.
        :rtype: bool
        """
        return all(cell.is_solved for cell in self._cells) and self.is_valid()

    def is_valid(self) -> bool:
        """Check that no house contains a duplicated solved digit.

        :returns: ``True`` if every row, column, and subgrid is valid.
        :rtype: bool
        """
        return all(unit.is_valid() for unit in self.units)

    # ------------------------------------------------------------------
    # Serialisation
    # ------------------------------------------------------------------
    def to_string(self, empty: str = ".") -> str:
        """Serialise the board to an 81-character single-line string.

        :param empty: The character used for unsolved cells.
        :type empty: str
        :returns: The board, left to right, top to bottom.
        :rtype: str
        """
        return "".join(
            str(cell.value) if cell.is_solved else empty for cell in self._cells
        )

    def __str__(self) -> str:
        """Render the board as a human-readable 9x9 diagram.

        :returns: A pretty-printed board with subgrid separators.
        :rtype: str
        """
        lines: list[str] = []
        for row_index, row in enumerate(self._rows):
            if row_index in (3, 6):
                lines.append("------+-------+------")
            chunks = []
            for start in range(0, 9, 3):
                chunks.append(
                    " ".join(
                        str(cell.value) if cell.is_solved else "."
                        for cell in row.cells[start:start + 3]
                    )
                )
            lines.append(" | ".join(chunks))
        return "\n".join(lines)

    def __repr__(self) -> str:
        """Return a debugging representation of the grid.

        :returns: A string reporting how many cells are solved.
        :rtype: str
        """
        solved = sum(1 for cell in self._cells if cell.is_solved)
        return f"<Grid {solved}/81 solved>"
