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
    AIC,
    AlsXz,
    AvoidableRectangle,
    BivalueUniversalGrave,
    FinnedSwordfish,
    FinnedXWing,
    ChuteRemotePairs,
    ClaimingCandidates,
    HiddenPair,
    HiddenQuad,
    HiddenSingle,
    HiddenTriple,
    Medusa3D,
    NakedPair,
    NakedQuad,
    NakedSingle,
    NakedTriple,
    Placement,
    PointingCandidates,
    SimpleColouring,
    Step,
    Swordfish,
    Technique,
    UniqueRectangle,
    UniqueRectangleType2,
    WWing,
    XChain,
    XWing,
    XYChain,
    XYZWing,
    YWing,
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
    :ivar grid: The board the session worked on, in its final state —
        solved, or holding the partial progress when the pipeline stalled.
    :vartype grid: Grid | None
    """

    solved: bool
    steps: tuple[Step, ...] = field(default=())
    grid: "Grid | None" = field(default=None)

    @property
    def used_backtracking(self) -> bool:
        """bool: Whether brute force contributed to this result.

        ``True`` only when the solver ran with the explicit backtracking
        fallback enabled *and* the logical techniques were not enough.
        """
        return any(step.technique == "Backtracking" for step in self.steps)

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
    :param assume_unique: When ``False``, uniqueness-based techniques
        (unique rectangles, BUG, avoidable rectangles) are excluded from
        the default pipeline, so solving stays sound on puzzles that may
        have multiple solutions. Ignored when ``techniques`` is given.
    :type assume_unique: bool
    :param backtracking_fallback: When ``True``, a puzzle the logical
        pipeline cannot finish is completed by brute-force search over
        the remaining candidates, recorded as an explicit
        ``"Backtracking"`` step. Off by default: logic only.
    :type backtracking_fallback: bool
    """

    def __init__(
        self,
        techniques: Sequence[Technique] | None = None,
        *,
        assume_unique: bool = True,
        backtracking_fallback: bool = False,
    ) -> None:
        self._techniques: tuple[Technique, ...] = (
            tuple(techniques)
            if techniques is not None
            else self.default_techniques(assume_unique=assume_unique)
        )
        self._backtracking_fallback = backtracking_fallback

    @staticmethod
    def default_techniques(*, assume_unique: bool = True) -> tuple[Technique, ...]:
        """Build the default pipeline, ordered from simplest to hardest.

        :param assume_unique: When ``False``, techniques flagged with
            :attr:`~dedoku.techniques.Technique.requires_unique_solution`
            are left out.
        :type assume_unique: bool
        :returns: Fresh instances of the selected techniques.
        :rtype: tuple[Technique, ...]
        """
        pipeline = (
            NakedSingle(),
            HiddenSingle(),
            NakedPair(),
            HiddenPair(),
            NakedTriple(),
            HiddenTriple(),
            NakedQuad(),
            HiddenQuad(),
            PointingCandidates(),
            ClaimingCandidates(),
            XWing(),
            ChuteRemotePairs(),
            SimpleColouring(),
            WWing(),
            YWing(),
            UniqueRectangle(),
            Swordfish(),
            XYZWing(),
            BivalueUniversalGrave(),
            AvoidableRectangle(),
            UniqueRectangleType2(),
            FinnedXWing(),
            FinnedSwordfish(),
            XChain(),
            XYChain(),
            Medusa3D(),
            AlsXz(),
            AIC(),
        )
        if assume_unique:
            return pipeline
        return tuple(
            technique for technique in pipeline
            if not technique.requires_unique_solution
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
        progress — unless the solver was built with
        ``backtracking_fallback=True``, in which case the remainder is
        completed by brute force and recorded as a ``"Backtracking"``
        step.

        :param grid: The board to solve.
        :type grid: Grid
        :returns: The session outcome with the full list of steps.
        :rtype: SolveResult
        :raises dedoku.exceptions.ContradictionError: If the board
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
        if not grid.is_solved() and self._backtracking_fallback:
            steps.extend(self._fall_back(grid, len(steps)))
        return SolveResult(
            solved=grid.is_solved(), steps=tuple(steps), grid=grid
        )

    @staticmethod
    def _fall_back(grid: Grid, logical_steps: int) -> tuple[Step, ...]:
        """Complete a stalled grid by brute force, as one explicit step.

        :param grid: The stalled board to complete in place.
        :type grid: Grid
        :param logical_steps: How many logical steps ran before the
            fallback (used in the step description).
        :type logical_steps: int
        :returns: A single ``"Backtracking"`` step listing every placed
            cell, or no steps when the board admits no completion.
        :rtype: tuple[Step, ...]
        :raises dedoku.exceptions.ContradictionError: If no completion
            exists, meaning the puzzle has no solution.
        """
        from .backtracking import complete_with_backtracking
        from .exceptions import ContradictionError

        pending = [cell for cell in grid.cells if not cell.is_solved]
        if not complete_with_backtracking(grid):
            raise ContradictionError(
                "the puzzle has no solution (backtracking found no "
                "completion)"
            )
        placements = tuple(
            Placement(cell.row_index, cell.column_index, cell.value)
            for cell in pending
            if cell.value is not None
        )
        if logical_steps:
            description = (
                f"logical techniques exhausted after {logical_steps} "
                f"steps; depth-first search filled the remaining "
                f"{len(placements)} cells"
            )
        else:
            description = (
                f"depth-first search filled all {len(placements)} cells"
            )
        return (
            Step(
                technique="Backtracking",
                description=description,
                placements=placements,
            ),
        )

    def __repr__(self) -> str:
        """Return a debugging representation of the solver.

        :returns: A string listing the pipeline size.
        :rtype: str
        """
        return f"<SudokuSolver with {len(self._techniques)} techniques>"
