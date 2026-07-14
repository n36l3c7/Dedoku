"""Unit tests for the Bivalue Universal Grave (BUG+1) technique."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid
from sudoku_solver.techniques import BivalueUniversalGrave


def _set_candidates(grid: Grid, position: tuple[int, int], keep: set[int]) -> None:
    """Reduce a cell's candidates to exactly ``keep``.

    :param grid: The board under construction.
    :type grid: Grid
    :param position: The ``(row, column)`` position of the cell.
    :type position: tuple[int, int]
    :param keep: The candidates the cell must retain.
    :type keep: set[int]
    """
    for digit in range(1, 10):
        if digit not in keep:
            grid.cell(*position).remove_candidate(digit)


def _build_bug_plus_one() -> Grid:
    """Sculpt a BUG+1 state around the trivalue cell R1C1 = {1, 2, 3}.

    Digit 1 appears exactly three times in the cell's row, column, and
    subgrid, while every other digit appears twice; every other cell of
    the board is bivalue.

    :returns: The sculpted board.
    :rtype: Grid
    """
    grid = Grid()
    pairs: dict[tuple[int, int], set[int]] = {
        # Row 1: digit 1 tripled, everything else twice.
        (0, 1): {4, 5}, (0, 2): {4, 5},
        (0, 3): {1, 2}, (0, 4): {1, 3},
        (0, 5): {6, 7}, (0, 6): {6, 7},
        (0, 7): {8, 9}, (0, 8): {8, 9},
        # Column 1: digit 1 tripled, everything else twice.
        (1, 0): {6, 7}, (2, 0): {6, 7},
        (3, 0): {1, 2}, (6, 0): {1, 3},
        (4, 0): {4, 5}, (5, 0): {4, 5},
        (7, 0): {8, 9}, (8, 0): {8, 9},
        # Rest of subgrid 1: digit 1 tripled, everything else twice.
        (1, 1): {1, 8}, (2, 2): {1, 9},
        (1, 2): {2, 8}, (2, 1): {3, 9},
    }
    _set_candidates(grid, (0, 0), {1, 2, 3})
    for position, pair in pairs.items():
        _set_candidates(grid, position, pair)
    for row_index in range(3, 9):
        for column_index in range(1, 9):
            _set_candidates(grid, (row_index, column_index), {8, 9})
    for row_index in (1, 2):
        for column_index in range(3, 9):
            _set_candidates(grid, (row_index, column_index), {8, 9})
    return grid


class BivalueUniversalGraveTests(unittest.TestCase):
    """A BUG+1 state is resolved by solving the trivalue cell."""

    def test_places_the_tripled_digit(self) -> None:
        """R1C1 takes 1, the only digit tripled in all three houses."""
        grid = _build_bug_plus_one()
        step = BivalueUniversalGrave().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "BUG")
        self.assertEqual(step.placements, ((0, 0, 1),))
        self.assertEqual(grid.cell(0, 0).value, 1)

    def test_non_bivalue_companion_disables_the_pattern(self) -> None:
        """A cell with a single candidate breaks the BUG+1 shape."""
        grid = _build_bug_plus_one()
        grid.cell(8, 8).remove_candidate(9)
        self.assertIsNone(BivalueUniversalGrave().apply(grid))

    def test_no_pattern_returns_none(self) -> None:
        """Boards that are not in a BUG+1 state are left untouched."""
        self.assertIsNone(BivalueUniversalGrave().apply(Grid()))
        nearly = Grid.from_string(
            "530070000600195000098000060800060003400803001"
            "700020006060000280000419005000080079"
        )
        self.assertIsNone(BivalueUniversalGrave().apply(nearly))


if __name__ == "__main__":
    unittest.main()
