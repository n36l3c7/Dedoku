"""The solving engine that chains logical techniques.

:class:`SudokuSolver` repeatedly walks an ordered pipeline of techniques,
always retrying from the simplest one after each successful deduction —
exactly how a human solver escalates only when the easy moves dry up.
The engine never guesses: if no technique applies, it stops and reports
a partial result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Sequence

from .techniques import (
    HiddenPair,
    HiddenQuad,
    HiddenSingle,
    HiddenTriple,
    NakedPair,
    NakedQuad,
    NakedSingle,
    NakedTriple,
    Step,
    Technique,
)

if TYPE_CHECKING:
    from .grid import Grid

__all__ = ["SolveResult", "SudokuSolver"]


@dataclass(frozen=True)
class SolveResult:
    """Outcome of a solving session.

    :ivar solved: Whether the puzzle was completely solved.
    :vartype solved: bool
    :ivar steps: Every deduction performed, in order of application.
    :vartype steps: tuple[Step, ...]
    """

    solved: bool
    steps: tuple[Step, ...] = field(default=())

    @property
    def techniques_used(self) -> tuple[str, ...]:
        """tuple[str, ...]: Distinct technique names, in first-use order."""
        return tuple(dict.fromkeys(step.technique for step in self.steps))


class SudokuSolver:
    """Logic-only Sudoku solver (no backtracking, no guessing).

    The solver owns an ordered pipeline of techniques. On every iteration
    it applies the first technique that produces a deduction, then starts
    over from the top of the pipeline, so harder strategies only run when
    the simpler ones are exhausted.

    :param techniques: Custom technique pipeline, tried in the given order.
        When omitted, :meth:`default_techniques` is used.
    :type techniques: Sequence[Technique] | None
    """

    def __init__(self, techniques: Sequence[Technique] | None = None) -> None:
        self._techniques: tuple[Technique, ...] = (
            tuple(techniques)
            if techniques is not None
            else self.default_techniques()
        )

    @staticmethod
    def default_techniques() -> tuple[Technique, ...]:
        """Build the default pipeline, ordered from simplest to hardest.

        :returns: Fresh instances of every implemented technique.
        :rtype: tuple[Technique, ...]
        """
        return (
            NakedSingle(),
            HiddenSingle(),
            NakedPair(),
            HiddenPair(),
            NakedTriple(),
            HiddenTriple(),
            NakedQuad(),
            HiddenQuad(),
        )

    @property
    def techniques(self) -> tuple[Technique, ...]:
        """tuple[Technique, ...]: The pipeline used by this solver."""
        return self._techniques

    def solve(self, grid: Grid) -> SolveResult:
        """Solve ``grid`` in place as far as pure logic allows.

        The grid is mutated: values are placed and candidates eliminated.
        When the pipeline runs dry before the board is complete, the
        result reports ``solved=False`` and the grid holds the partial
        progress, ready for inspection or for a retry with a stronger
        pipeline.

        :param grid: The board to solve.
        :type grid: Grid
        :returns: The session outcome with the full list of steps.
        :rtype: SolveResult
        :raises sudoku_solver.exceptions.ContradictionError: If the board
            reaches an impossible state, meaning the puzzle has no solution.
        """
        steps: list[Step] = []
        while not grid.is_solved():
            for technique in self._techniques:
                step = technique.apply(grid)
                if step is not None:
                    steps.append(step)
                    break
            else:
                break
        return SolveResult(solved=grid.is_solved(), steps=tuple(steps))

    def __repr__(self) -> str:
        """Return a debugging representation of the solver.

        :returns: A string listing the pipeline size.
        :rtype: str
        """
        return f"<SudokuSolver with {len(self._techniques)} techniques>"
