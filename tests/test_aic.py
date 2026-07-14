"""Unit tests for the Alternating Inference Chain technique."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid
from sudoku_solver.techniques import AIC


class AICTests(unittest.TestCase):
    """General chains subsume the dedicated wing/chain patterns."""

    def test_w_wing_shape_found_as_aic(self) -> None:
        """The W-Wing pattern falls to a five-link AIC.

        {1,2} at R1C1 and R5C4 with a conjugate pair on 2 in column 9:
        1@R1C1 = 2@R1C1 - 2@R1C9 = 2@R5C9 - 2@R5C4 = 1@R5C4. One
        endpoint holds 1, so R1C4 and R5C1 lose it.
        """
        grid = Grid()
        for digit in range(1, 10):
            if digit not in (1, 2):
                grid.cell(0, 0).remove_candidate(digit)
                grid.cell(4, 3).remove_candidate(digit)
        for row_index in range(9):
            if row_index not in (0, 4):
                grid.cell(row_index, 8).remove_candidate(2)
        step = AIC().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "AIC")
        self.assertEqual(
            set(step.eliminations), {(0, 3, 1), (4, 0, 1)}
        )
        self.assertNotIn(1, grid.cell(0, 3).candidates)
        self.assertNotIn(1, grid.cell(4, 0).candidates)
        # The pattern cells keep their candidates.
        self.assertEqual(grid.cell(0, 0).candidates, frozenset({1, 2}))
        self.assertEqual(grid.cell(4, 3).candidates, frozenset({1, 2}))

    def test_no_pattern_returns_none(self) -> None:
        """An empty board has no strong links, hence no chains."""
        self.assertIsNone(AIC().apply(Grid()))


if __name__ == "__main__":
    unittest.main()
