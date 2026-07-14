"""Unit tests for :mod:`sudoku_solver.cell`."""

from __future__ import annotations

import unittest

from sudoku_solver import Cell, ContradictionError, DIGITS, Grid


class CellStateTests(unittest.TestCase):
    """Behaviour of a cell's value, candidates, and flags."""

    def setUp(self) -> None:
        """Create an empty grid for each test."""
        self.grid = Grid()

    def test_new_cell_is_unsolved_with_all_candidates(self) -> None:
        """A fresh cell has no value and all nine candidates."""
        cell = self.grid.cell(0, 0)
        self.assertIsNone(cell.value)
        self.assertFalse(cell.is_solved)
        self.assertEqual(cell.candidates, DIGITS)

    def test_position_and_label(self) -> None:
        """Position accessors expose zero-based indices, labels are one-based."""
        cell = self.grid.cell(3, 6)
        self.assertEqual(cell.position, (3, 6))
        self.assertEqual(cell.row_index, 3)
        self.assertEqual(cell.column_index, 6)
        self.assertEqual(cell.label, "R4C7")

    def test_invalid_position_is_rejected(self) -> None:
        """Cells outside the 9x9 board cannot be created."""
        with self.assertRaises(ValueError):
            Cell(9, 0)
        with self.assertRaises(ValueError):
            Cell(0, -1)

    def test_is_bivalue(self) -> None:
        """A cell with exactly two candidates is flagged as bivalue."""
        cell = self.grid.cell(0, 0)
        self.assertFalse(cell.is_bivalue)
        for digit in range(3, 10):
            cell.remove_candidate(digit)
        self.assertTrue(cell.is_bivalue)


class CellPeersTests(unittest.TestCase):
    """Peer computation across row, column, and subgrid."""

    def test_peers_count_and_membership(self) -> None:
        """A cell has 20 distinct peers covering its three houses."""
        grid = Grid()
        cell = grid.cell(4, 4)
        peers = cell.peers
        self.assertEqual(len(peers), 20)
        self.assertNotIn(cell, peers)
        positions = {peer.position for peer in peers}
        self.assertIn((4, 0), positions)   # same row
        self.assertIn((0, 4), positions)   # same column
        self.assertIn((3, 3), positions)   # same subgrid


class CellMutationTests(unittest.TestCase):
    """Placing values and eliminating candidates."""

    def setUp(self) -> None:
        """Create an empty grid for each test."""
        self.grid = Grid()

    def test_set_value_propagates_to_peers(self) -> None:
        """Placing a digit removes it from the candidates of all peers."""
        cell = self.grid.cell(0, 0)
        cell.set_value(5)
        self.assertEqual(cell.value, 5)
        self.assertEqual(cell.candidates, frozenset())
        for peer in cell.peers:
            self.assertNotIn(5, peer.candidates)

    def test_set_value_twice_is_rejected(self) -> None:
        """A solved cell cannot be assigned again."""
        cell = self.grid.cell(0, 0)
        cell.set_value(5)
        with self.assertRaises(ValueError):
            cell.set_value(6)

    def test_set_value_requires_a_candidate(self) -> None:
        """Placing a digit that is not a candidate raises a contradiction."""
        cell = self.grid.cell(0, 0)
        self.grid.cell(0, 1).set_value(5)
        with self.assertRaises(ContradictionError):
            cell.set_value(5)

    def test_invalid_digit_is_rejected(self) -> None:
        """Digits outside 1-9 are rejected everywhere."""
        cell = self.grid.cell(0, 0)
        with self.assertRaises(ValueError):
            cell.set_value(0)
        with self.assertRaises(ValueError):
            cell.remove_candidate(10)

    def test_remove_candidate_reports_change(self) -> None:
        """remove_candidate returns True only when something was removed."""
        cell = self.grid.cell(0, 0)
        self.assertTrue(cell.remove_candidate(1))
        self.assertFalse(cell.remove_candidate(1))

    def test_removing_last_candidate_is_a_contradiction(self) -> None:
        """Stripping the final candidate raises ContradictionError."""
        cell = self.grid.cell(0, 0)
        for digit in range(1, 9):
            cell.remove_candidate(digit)
        with self.assertRaises(ContradictionError):
            cell.remove_candidate(9)


if __name__ == "__main__":
    unittest.main()
