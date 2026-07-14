"""Tests for the command-line interface."""

from __future__ import annotations

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

from dedoku.cli import main

EASY_PUZZLE = (
    "530070000600195000098000060800060003400803001"
    "700020006060000280000419005000080079"
)
EXTREME_PUZZLE = (  # AI Escargot: beyond the logical pipeline
    "1....7.9..3..2...8..96..5....53..9...1..8...2"
    "6....4...3......1..4......7..7...3.."
)


class CliTests(unittest.TestCase):
    """The dedoku command solves, explains, and reports failures."""

    def test_solves_and_prints_the_board(self) -> None:
        """A solvable puzzle exits 0 and prints the solved board."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([EASY_PUZZLE])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("5 3 4 | 6 7 8 | 9 1 2", text)
        self.assertIn("Solved in", text)

    def test_explain_prints_every_step(self) -> None:
        """--explain logs one numbered line per deduction."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([EASY_PUZZLE, "--explain"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("[Naked Single]", text)
        self.assertIn(" = ", text)  # placements shown as RxCy = digit
        self.assertIn("   1. ", text)

    def test_stalled_puzzle_exits_one(self) -> None:
        """A puzzle beyond the pipeline exits 1 with a clear message."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([EXTREME_PUZZLE])
        self.assertEqual(code, 1)
        self.assertIn("Not fully solvable", out.getvalue())

    def test_invalid_puzzle_exits_two(self) -> None:
        """Malformed input exits 2 and reports on stderr."""
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(["123"])
        self.assertEqual(code, 2)
        self.assertIn("error:", err.getvalue())

    def test_multi_flag_is_accepted(self) -> None:
        """--multi still solves puzzles not needing uniqueness logic."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([EASY_PUZZLE, "--multi"])
        self.assertEqual(code, 0)

    def test_hybrid_method_finishes_extreme_puzzles(self) -> None:
        """--method hybrid completes what pure logic cannot."""
        out = io.StringIO()
        with redirect_stdout(out):
            code = main([EXTREME_PUZZLE, "--method", "hybrid", "-e"])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("[Backtracking]", text)
        self.assertIn("Solved in", text)


if __name__ == "__main__":
    unittest.main()
