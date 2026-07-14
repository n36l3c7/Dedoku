"""Unit tests for the Simple Colouring technique."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid
from sudoku_solver.techniques import SimpleColouring


def _limit_homes(grid: Grid, digit: int, unit_cells, keep) -> None:
    """Remove ``digit`` from every cell of ``unit_cells`` not in ``keep``.

    :param grid: The board under construction.
    :type grid: Grid
    :param digit: The digit to restrict.
    :type digit: int
    :param unit_cells: Iterable of ``(row, column)`` positions of a house.
    :param keep: Positions allowed to keep the digit.
    """
    for row_index, column_index in unit_cells:
        if (row_index, column_index) not in keep:
            grid.cell(row_index, column_index).remove_candidate(digit)


class ColourWrapTests(unittest.TestCase):
    """Two same-colour cells seeing each other falsify the whole colour."""

    def test_wrap_eliminates_false_colour(self) -> None:
        """A four-link chain with a same-colour clash clears that colour.

        Chain on digit 5: R1C1-R1C5 (row 1), R1C5-R7C5 (column 5),
        R7C5-R9C4 (subgrid 8), R9C4-R9C1 (row 9). Colours alternate, so
        R1C1, R7C5, and R9C1 share one colour; R1C1 and R9C1 both lie in
        column 1, which wraps the colour and removes 5 from all three.
        """
        grid = Grid()
        _limit_homes(
            grid, 5, ((0, c) for c in range(9)), {(0, 0), (0, 4)}
        )
        _limit_homes(
            grid, 5, ((r, 4) for r in range(9)), {(0, 4), (6, 4)}
        )
        _limit_homes(
            grid,
            5,
            ((r, c) for r in (6, 7, 8) for c in (3, 4, 5)),
            {(6, 4), (8, 3)},
        )
        _limit_homes(
            grid, 5, ((8, c) for c in range(9)), {(8, 3), (8, 0)}
        )
        step = SimpleColouring().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Simple Colouring")
        for row_index, column_index in ((0, 0), (6, 4), (8, 0)):
            self.assertNotIn(
                5, grid.cell(row_index, column_index).candidates
            )
        for row_index, column_index in ((0, 4), (8, 3)):
            self.assertIn(
                5, grid.cell(row_index, column_index).candidates
            )

    def test_no_pattern_returns_none(self) -> None:
        """An empty board has no conjugate links at all."""
        self.assertIsNone(SimpleColouring().apply(Grid()))


class ColourTrapTests(unittest.TestCase):
    """An uncoloured cell seeing both colours loses the digit."""

    def test_trap_eliminates_outside_cell(self) -> None:
        """A three-link chain traps R9C1, which sees both chain colours.

        Chain on digit 5: R1C1-R1C5 (row 1), R1C5-R7C5 (column 5),
        R7C5-R9C4 (subgrid 8). R9C1 sees R1C1 (column 1, one colour) and
        R9C4 (row 9, opposite colour), so 5 is removed from R9C1 only.
        """
        grid = Grid()
        _limit_homes(
            grid, 5, ((0, c) for c in range(9)), {(0, 0), (0, 4)}
        )
        _limit_homes(
            grid, 5, ((r, 4) for r in range(9)), {(0, 4), (6, 4)}
        )
        _limit_homes(
            grid,
            5,
            ((r, c) for r in (6, 7, 8) for c in (3, 4, 5)),
            {(6, 4), (8, 3)},
        )
        step = SimpleColouring().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Simple Colouring")
        self.assertEqual(step.eliminations, ((8, 0, 5),))
        self.assertNotIn(5, grid.cell(8, 0).candidates)
        # Chain cells keep the digit.
        for row_index, column_index in ((0, 0), (0, 4), (6, 4), (8, 3)):
            self.assertIn(
                5, grid.cell(row_index, column_index).candidates
            )


if __name__ == "__main__":
    unittest.main()
