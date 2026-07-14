"""Unit tests for the naked and hidden candidate techniques."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid
from sudoku_solver.techniques import (
    HiddenPair,
    HiddenSingle,
    NakedPair,
    NakedSingle,
)


class NakedSingleTests(unittest.TestCase):
    """Cells reduced to one candidate get solved."""

    def test_places_the_only_candidate(self) -> None:
        """A cell left with one candidate receives it, peers are updated."""
        grid = Grid()
        cell = grid.cell(4, 4)
        for digit in range(1, 9):
            cell.remove_candidate(digit)
        step = NakedSingle().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Naked Single")
        self.assertEqual(step.placements, ((4, 4, 9),))
        self.assertEqual(cell.value, 9)
        for peer in cell.peers:
            self.assertNotIn(9, peer.candidates)

    def test_no_pattern_returns_none(self) -> None:
        """An empty board offers no naked single."""
        self.assertIsNone(NakedSingle().apply(Grid()))


class NakedPairTests(unittest.TestCase):
    """Two cells sharing two candidates clear those digits from the house."""

    def test_eliminates_pair_digits_from_unit(self) -> None:
        """A {1, 2} pair in row 1 strips 1 and 2 from the rest of the row."""
        grid = Grid()
        for digit in range(3, 10):
            grid.cell(0, 0).remove_candidate(digit)
            grid.cell(0, 1).remove_candidate(digit)
        step = NakedPair().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Naked Pair")
        self.assertGreater(len(step.eliminations), 0)
        for column_index in range(2, 9):
            candidates = grid.cell(0, column_index).candidates
            self.assertNotIn(1, candidates)
            self.assertNotIn(2, candidates)
        # The pair cells themselves keep their two candidates.
        self.assertEqual(grid.cell(0, 0).candidates, frozenset({1, 2}))
        self.assertEqual(grid.cell(0, 1).candidates, frozenset({1, 2}))

    def test_no_pattern_returns_none(self) -> None:
        """An empty board offers no naked pair."""
        self.assertIsNone(NakedPair().apply(Grid()))


class HiddenSingleTests(unittest.TestCase):
    """Digits with a single home in a house get placed."""

    def test_places_digit_with_one_home(self) -> None:
        """If 5 fits only in R1C1 within row 1, it is placed there."""
        grid = Grid()
        for column_index in range(1, 9):
            grid.cell(0, column_index).remove_candidate(5)
        step = HiddenSingle().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Hidden Single")
        self.assertEqual(step.placements, ((0, 0, 5),))
        self.assertEqual(grid.cell(0, 0).value, 5)

    def test_no_pattern_returns_none(self) -> None:
        """An empty board offers no hidden single."""
        self.assertIsNone(HiddenSingle().apply(Grid()))


class HiddenPairTests(unittest.TestCase):
    """Two digits confined to two cells strip their other candidates."""

    def test_confines_cells_to_the_pair(self) -> None:
        """If 1 and 2 fit only in R1C1/R1C2, those cells keep only {1, 2}."""
        grid = Grid()
        for column_index in range(2, 9):
            grid.cell(0, column_index).remove_candidate(1)
            grid.cell(0, column_index).remove_candidate(2)
        step = HiddenPair().apply(grid)
        self.assertIsNotNone(step)
        self.assertEqual(step.technique, "Hidden Pair")
        self.assertGreater(len(step.eliminations), 0)
        self.assertEqual(grid.cell(0, 0).candidates, frozenset({1, 2}))
        self.assertEqual(grid.cell(0, 1).candidates, frozenset({1, 2}))

    def test_no_pattern_returns_none(self) -> None:
        """An empty board offers no hidden pair."""
        self.assertIsNone(HiddenPair().apply(Grid()))


if __name__ == "__main__":
    unittest.main()
