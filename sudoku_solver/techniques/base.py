"""Framework shared by every logical solving technique.

A technique inspects the board and, when its pattern is found, mutates the
grid (placing a value or eliminating candidates) and reports what it did as
an immutable :class:`Step`. The solver chains these steps until the puzzle
is solved or no technique applies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..grid import Grid

__all__ = ["Step", "Technique"]


@dataclass(frozen=True)
class Step:
    """Immutable record of one successful technique application.

    Coordinates are zero-based ``(row_index, column_index, digit)`` triples;
    the human-readable :attr:`description` uses one-based ``RxCy`` labels.

    :ivar technique: Name of the technique that produced the step.
    :vartype technique: str
    :ivar description: Human-readable explanation of the deduction.
    :vartype description: str
    :ivar placements: Values placed on the board by this step.
    :vartype placements: tuple[tuple[int, int, int], ...]
    :ivar eliminations: Candidates removed from cells by this step.
    :vartype eliminations: tuple[tuple[int, int, int], ...]
    """

    technique: str
    description: str
    placements: tuple[tuple[int, int, int], ...] = field(default=())
    eliminations: tuple[tuple[int, int, int], ...] = field(default=())


class Technique(ABC):
    """Abstract base class for a single logical solving strategy.

    Concrete techniques must be stateless: all information lives in the
    grid, so the same instance can be reused across puzzles.

    :cvar name: Human-readable technique name shown in solving reports.
    """

    name: str = "technique"

    @abstractmethod
    def apply(self, grid: Grid) -> Step | None:
        """Search the grid and apply the first occurrence of the pattern.

        Implementations must mutate the grid **only** when they return a
        step, and each call must perform at most one deduction so that the
        solver can always fall back to the simplest available technique.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: A record of the deduction, or ``None`` if the pattern
            does not occur anywhere on the board.
        :rtype: Step | None
        :raises sudoku_solver.exceptions.ContradictionError: If applying
            the deduction reveals an inconsistent board state.
        """

    def __repr__(self) -> str:
        """Return a debugging representation of the technique.

        :returns: A string such as ``<Technique 'Naked Pair'>``.
        :rtype: str
        """
        return f"<Technique {self.name!r}>"
