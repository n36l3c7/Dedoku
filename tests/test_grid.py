"""Unit tests for :mod:`sudoku_solver.grid` and :mod:`sudoku_solver.units`."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid, InvalidGridError

PUZZLE = (
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


class GridConstructionTests(unittest.TestCase):
    """Building grids from scratch and from strings."""

    def test_empty_grid_shape(self) -> None:
        """An empty grid wires 81 cells into 27 houses of nine cells each."""
        grid = Grid()
        self.assertEqual(len(grid.cells), 81)
        self.assertEqual(len(grid.units), 27)
        for unit in grid.units:
            self.assertEqual(len(unit), 9)

    def test_subgrid_index_mapping(self) -> None:
        """Subgrids are indexed left to right, top to bottom."""
        self.assertEqual(Grid.subgrid_index(0, 0), 0)
        self.assertEqual(Grid.subgrid_index(0, 8), 2)
        self.assertEqual(Grid.subgrid_index(4, 4), 4)
        self.assertEqual(Grid.subgrid_index(8, 0), 6)
        self.assertEqual(Grid.subgrid_index(8, 8), 8)

    def test_cell_unit_wiring(self) -> None:
        """Each cell references the row, column, and subgrid that contain it."""
        grid = Grid()
        cell = grid.cell(4, 7)
        self.assertIs(cell.row, grid.rows[4])
        self.assertIs(cell.column, grid.columns[7])
        self.assertIs(cell.subgrid, grid.subgrids[5])
        self.assertIn(cell, cell.row.cells)
        self.assertIn(cell, cell.column.cells)
        self.assertIn(cell, cell.subgrid.cells)

    def test_from_string_places_givens(self) -> None:
        """Givens are placed and serialisation round-trips."""
        grid = Grid.from_string(PUZZLE)
        self.assertEqual(grid.cell(0, 0).value, 5)
        self.assertEqual(grid.cell(2, 1).value, 9)
        self.assertIsNone(grid.cell(0, 2).value)
        self.assertEqual(grid.to_string(empty="0"), PUZZLE)

    def test_from_string_accepts_pretty_format(self) -> None:
        """The output of str(grid) can be parsed back."""
        grid = Grid.from_string(PUZZLE)
        reparsed = Grid.from_string(str(grid))
        self.assertEqual(reparsed.to_string(), grid.to_string())

    def test_from_string_rejects_wrong_length(self) -> None:
        """Descriptions without exactly 81 cells are rejected."""
        with self.assertRaises(InvalidGridError):
            Grid.from_string("123")

    def test_from_string_rejects_unknown_characters(self) -> None:
        """Characters outside the accepted alphabet are rejected."""
        with self.assertRaises(InvalidGridError):
            Grid.from_string("x" * 81)

    def test_from_string_rejects_contradictory_givens(self) -> None:
        """Two identical digits in one house make the puzzle invalid."""
        contradictory = "55" + "0" * 79
        with self.assertRaises(InvalidGridError):
            Grid.from_string(contradictory)


class GridStateTests(unittest.TestCase):
    """Validity and completion checks."""

    def test_candidates_reflect_givens(self) -> None:
        """Candidates of empty cells exclude digits seen in their houses."""
        grid = Grid.from_string(PUZZLE)
        candidates = grid.cell(0, 2).candidates
        self.assertNotIn(5, candidates)  # same row and subgrid
        self.assertNotIn(9, candidates)  # same column and subgrid
        self.assertIn(1, candidates)

    def test_unit_bookkeeping(self) -> None:
        """Units report solved digits, missing digits, and candidate homes."""
        grid = Grid.from_string(PUZZLE)
        row = grid.rows[0]
        self.assertEqual(row.solved_values(), frozenset({5, 3, 7}))
        self.assertEqual(row.missing_values(), frozenset({1, 2, 4, 6, 8, 9}))
        self.assertEqual(len(row.unsolved_cells()), 6)
        for cell in row.cells_with_candidate(1):
            self.assertIn(1, cell.candidates)

    def test_fresh_puzzle_is_valid_but_unsolved(self) -> None:
        """A well-formed puzzle starts valid and incomplete."""
        grid = Grid.from_string(PUZZLE)
        self.assertTrue(grid.is_valid())
        self.assertFalse(grid.is_solved())


if __name__ == "__main__":
    unittest.main()
