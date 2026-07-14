"""Tests for the opt-in backtracking fallback and solving modes."""

from __future__ import annotations

import unittest

import dedoku
from dedoku import ContradictionError, Grid, SudokuSolver
from dedoku.backtracking import complete_with_backtracking

from tests.support import solve_backtracking

EASY_PUZZLE = (
    "530070000600195000098000060800060003400803001"
    "700020006060000280000419005000080079"
)
EXTREME_PUZZLE = (  # AI Escargot: beyond the logical pipeline
    "1....7.9..3..2...8..96..5....53..9...1..8...2"
    "6....4...3......1..4......7..7...3.."
)


class HybridModeTests(unittest.TestCase):
    """Techniques first, brute force only for the residue."""

    def test_hybrid_finishes_an_extreme_puzzle(self) -> None:
        """AI Escargot finally solves, with an explicit fallback step."""
        result = dedoku.solve(EXTREME_PUZZLE, method="hybrid")
        self.assertTrue(result.solved)
        self.assertTrue(result.used_backtracking)
        assert result.grid is not None
        self.assertEqual(
            result.grid.to_string(), solve_backtracking(EXTREME_PUZZLE)
        )
        last = result.steps[-1]
        self.assertEqual(last.technique, "Backtracking")
        self.assertGreater(len(last.placements), 0)
        self.assertIn("Backtracking", result.techniques_used)

    def test_hybrid_stays_logical_when_logic_suffices(self) -> None:
        """A puzzle logic can finish never touches the fallback."""
        result = dedoku.solve(EASY_PUZZLE, method="hybrid")
        self.assertTrue(result.solved)
        self.assertFalse(result.used_backtracking)


class BacktrackingModeTests(unittest.TestCase):
    """Direct brute force, chosen up front."""

    def test_backtracking_mode_solves_without_techniques(self) -> None:
        """The whole board is filled by a single Backtracking step."""
        result = dedoku.solve(EASY_PUZZLE, method="backtracking")
        self.assertTrue(result.solved)
        self.assertEqual(len(result.steps), 1)
        self.assertEqual(result.steps[0].technique, "Backtracking")
        assert result.grid is not None
        self.assertEqual(
            result.grid.to_string(), solve_backtracking(EASY_PUZZLE)
        )

    def test_unknown_method_is_rejected(self) -> None:
        """An unknown method name raises ValueError."""
        with self.assertRaises(ValueError):
            dedoku.solve(EASY_PUZZLE, method="guess")


class DefaultsUnchangedTests(unittest.TestCase):
    """Logic-only remains the default everywhere."""

    def test_default_still_stalls_on_extreme(self) -> None:
        """Without opting in, the library never guesses."""
        result = dedoku.solve(EXTREME_PUZZLE)
        self.assertFalse(result.solved)
        self.assertFalse(result.used_backtracking)

    def test_solver_class_default_has_no_fallback(self) -> None:
        """SudokuSolver() alone never produces a Backtracking step."""
        grid = Grid.from_string(EXTREME_PUZZLE)
        result = SudokuSolver().solve(grid)
        self.assertFalse(result.used_backtracking)


class CompletionFunctionTests(unittest.TestCase):
    """The low-level completion respects candidates and reports failure."""

    def test_reports_unsolvable_state(self) -> None:
        """Removing a true digit's candidate makes completion impossible."""
        grid = Grid.from_string(EASY_PUZZLE)
        solution = solve_backtracking(EASY_PUZZLE)
        target = next(cell for cell in grid.cells if not cell.is_solved)
        true_digit = int(solution[target.row_index * 9 + target.column_index])
        target.remove_candidate(true_digit)
        self.assertFalse(complete_with_backtracking(grid))

    def test_solver_raises_on_unsolvable_state(self) -> None:
        """The fallback surfaces impossibility as ContradictionError."""
        grid = Grid.from_string(EXTREME_PUZZLE)
        solution = solve_backtracking(EXTREME_PUZZLE)
        target = next(cell for cell in grid.cells if not cell.is_solved)
        true_digit = int(solution[target.row_index * 9 + target.column_index])
        target.remove_candidate(true_digit)
        solver = SudokuSolver(techniques=(), backtracking_fallback=True)
        with self.assertRaises(ContradictionError):
            solver.solve(grid)


if __name__ == "__main__":
    unittest.main()
