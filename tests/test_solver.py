"""End-to-end tests for :class:`sudoku_solver.solver.SudokuSolver`."""

from __future__ import annotations

import unittest

from sudoku_solver import Grid, SudokuSolver

EASY_PUZZLE = (
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

EASY_SOLUTION = (
    "534678912"
    "672195348"
    "198342567"
    "859761423"
    "426853791"
    "713924856"
    "961537284"
    "287419635"
    "345286179"
)

# "AI Escargot": far beyond naked/hidden subsets, must yield a partial result.
EXTREME_PUZZLE = (
    "1....7.9."
    ".3..2...8"
    "..96..5.."
    "..53..9.."
    ".1..8...2"
    "6....4..."
    "3......1."
    ".4......7"
    "..7...3.."
)


class SolverTests(unittest.TestCase):
    """Solving sessions with the default pipeline."""

    def test_solves_easy_puzzle(self) -> None:
        """A singles-level puzzle is fully solved and matches the solution."""
        grid = Grid.from_string(EASY_PUZZLE)
        result = SudokuSolver().solve(grid)
        self.assertTrue(result.solved)
        self.assertTrue(grid.is_solved())
        self.assertEqual(grid.to_string(), EASY_SOLUTION)
        self.assertGreater(len(result.steps), 0)

    def test_steps_are_reported(self) -> None:
        """Every step names its technique and describes the deduction."""
        grid = Grid.from_string(EASY_PUZZLE)
        result = SudokuSolver().solve(grid)
        for step in result.steps:
            self.assertTrue(step.technique)
            self.assertTrue(step.description)
            self.assertTrue(step.placements or step.eliminations)
        self.assertIn("Naked Single", result.techniques_used)

    def test_already_solved_grid(self) -> None:
        """A complete board yields a solved result with zero steps."""
        grid = Grid.from_string(EASY_SOLUTION)
        result = SudokuSolver().solve(grid)
        self.assertTrue(result.solved)
        self.assertEqual(result.steps, ())

    def test_extreme_puzzle_stops_without_guessing(self) -> None:
        """When logic runs dry the solver stops with a valid partial board."""
        grid = Grid.from_string(EXTREME_PUZZLE)
        result = SudokuSolver().solve(grid)
        self.assertFalse(result.solved)
        self.assertFalse(grid.is_solved())
        self.assertTrue(grid.is_valid())

    def test_custom_pipeline_is_respected(self) -> None:
        """A solver built with an explicit pipeline uses exactly that."""
        from sudoku_solver.techniques import NakedSingle

        solver = SudokuSolver(techniques=[NakedSingle()])
        self.assertEqual(len(solver.techniques), 1)
        grid = Grid.from_string(EASY_PUZZLE)
        result = solver.solve(grid)
        self.assertEqual(
            set(result.techniques_used) or {"Naked Single"}, {"Naked Single"}
        )


if __name__ == "__main__":
    unittest.main()
