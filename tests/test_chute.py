"""Unit tests for the Chute Remote Pairs technique."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid
from sudoku_solver.techniques import ChuteRemotePairs


class ChuteRemotePairsTests(unittest.TestCase):
    """Two same-pair cells in a chute plus an absent digit eliminate."""

    def test_band_remote_pair_eliminates_present_digit(self) -> None:
        """{1, 2} at R1C1/R2C4 with 1 absent from the blind cells kills 2.

        The blind cells (seeing neither pair cell) are R3C7, R3C8, and
        R3C9: the remaining row of band 1 inside the remaining subgrid.
        """
        grid = Grid()
        for digit in range(3, 10):
            grid.cell(0, 0).remove_candidate(digit)
            grid.cell(1, 3).remove_candidate(digit)
        for column_index in (6, 7, 8):
            grid.cell(2, column_index).remove_candidate(1)
        step = ChuteRemotePairs().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Chute Remote Pairs")
        self.assertGreater(len(step.eliminations), 0)
        # Cells seeing both R1C1 and R2C4 lose digit 2.
        for row_index, column_index in (
            (0, 3), (0, 4), (0, 5), (1, 0), (1, 1), (1, 2),
        ):
            self.assertNotIn(
                2, grid.cell(row_index, column_index).candidates
            )
        # The pair cells themselves are untouched.
        self.assertEqual(grid.cell(0, 0).candidates, frozenset({1, 2}))
        self.assertEqual(grid.cell(1, 3).candidates, frozenset({1, 2}))

    def test_no_pattern_returns_none(self) -> None:
        """Without an absent digit in the blind cells nothing happens."""
        grid = Grid()
        for digit in range(3, 10):
            grid.cell(0, 0).remove_candidate(digit)
            grid.cell(1, 3).remove_candidate(digit)
        self.assertIsNone(ChuteRemotePairs().apply(grid))
        self.assertIsNone(ChuteRemotePairs().apply(Grid()))


if __name__ == "__main__":
    unittest.main()
