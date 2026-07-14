"""Command-line interface.

Run ``dedoku`` (or ``python -m dedoku``) with an 81-character puzzle to
solve it with pure logic. With ``--explain`` every deduction is printed in
order, showing exactly how each cell was filled and which candidates were
eliminated along the way.

Exit codes: ``0`` solved, ``1`` not fully solvable by the logical
pipeline, ``2`` invalid input.
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

from . import __version__, solve
from .exceptions import SudokuError

__all__ = ["build_parser", "main"]


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the ``dedoku`` command.

    :returns: The configured parser.
    :rtype: argparse.ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="dedoku",
        description=(
            "Solve a Sudoku with human-style logical deduction - "
            "no backtracking, no guessing."
        ),
    )
    parser.add_argument(
        "puzzle",
        nargs="?",
        help=(
            "81-character puzzle, digits 1-9 for givens and 0 or . for "
            "blanks; omitted, the puzzle is read from standard input"
        ),
    )
    parser.add_argument(
        "-e", "--explain",
        action="store_true",
        help="print every deduction in order before the final board",
    )
    parser.add_argument(
        "--method",
        choices=("logic", "hybrid", "backtracking"),
        default="logic",
        help=(
            "logic (default): explainable techniques only, may stall on "
            "the hardest puzzles; hybrid: techniques first, brute force "
            "completes any remainder; backtracking: brute force directly"
        ),
    )
    parser.add_argument(
        "--multi",
        action="store_true",
        help=(
            "do not assume the puzzle has a unique solution "
            "(disables uniqueness-based techniques)"
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"dedoku {__version__}",
    )
    return parser


def _describe(step_number: int, technique: str, description: str,
              what: str) -> str:
    """Format one line of the ``--explain`` log.

    :param step_number: One-based step counter.
    :type step_number: int
    :param technique: The technique name.
    :type technique: str
    :param description: The step's human-readable explanation.
    :type description: str
    :param what: Compact summary of the effect (placement or removals).
    :type what: str
    :returns: The formatted line.
    :rtype: str
    """
    return f"{step_number:4d}. {what:<22} [{technique}] {description}"


def main(argv: Sequence[str] | None = None) -> int:
    """Run the command-line interface.

    :param argv: Argument list; defaults to ``sys.argv[1:]``.
    :type argv: Sequence[str] | None
    :returns: The process exit code.
    :rtype: int
    """
    args = build_parser().parse_args(argv)
    text = args.puzzle if args.puzzle is not None else sys.stdin.read()
    try:
        result = solve(
            text, method=args.method, assume_unique=not args.multi
        )
    except SudokuError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.explain:
        for number, step in enumerate(result.steps, start=1):
            if step.placements:
                what = ", ".join(
                    f"R{p.row + 1}C{p.column + 1} = {p.digit}"
                    for p in step.placements
                )
            else:
                count = len(step.eliminations)
                plural = "s" if count != 1 else ""
                what = f"removes {count} candidate{plural}"
            print(_describe(number, step.technique, step.description, what))
        print()
    print(result.grid)
    if result.solved:
        techniques = ", ".join(result.techniques_used)
        print(f"\nSolved in {len(result.steps)} steps using: {techniques}")
        return 0
    print(
        f"\nNot fully solvable by pure logic: {len(result.steps)} steps "
        f"applied, then no technique makes further progress."
    )
    return 1
