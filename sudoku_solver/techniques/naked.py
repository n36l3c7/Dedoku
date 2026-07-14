"""Naked candidate techniques: Single, Pair, Triple, and Quad.

A *naked* subset is a group of ``n`` unsolved cells inside one house whose
candidates, taken together, span exactly ``n`` digits. Those digits must go
into those cells, so they can be eliminated from every other cell of the
house. With ``n = 1`` the cell simply receives its only candidate.
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from .base import Step, Technique

if TYPE_CHECKING:
    from ..grid import Grid

__all__ = ["NakedSingle", "NakedPair", "NakedTriple", "NakedQuad"]


class NakedSingle(Technique):
    """Place the value of any cell left with a single candidate."""

    name = "Naked Single"

    def apply(self, grid: Grid) -> Step | None:
        """Find the first cell with exactly one candidate and solve it.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The placement performed, or ``None`` if every unsolved
            cell still has two or more candidates.
        :rtype: Step | None
        """
        for cell in grid.cells:
            if cell.is_solved or len(cell.candidates) != 1:
                continue
            digit = next(iter(cell.candidates))
            cell.set_value(digit)
            return Step(
                technique=self.name,
                description=f"{cell.label} has {digit} as its only candidate",
                placements=((cell.row_index, cell.column_index, digit),),
            )
        return None


class _NakedSubset(Technique):
    """Shared implementation for naked pairs, triples, and quads.

    :cvar size: Number of cells (and digits) forming the subset.
    :cvar subset_word: Human-readable subset name used in descriptions.
    """

    size: int = 0
    subset_word: str = ""

    def apply(self, grid: Grid) -> Step | None:
        """Find the first naked subset that eliminates at least one candidate.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The eliminations performed, or ``None`` if no productive
            naked subset of this size exists.
        :rtype: Step | None
        """
        for unit in grid.units:
            unsolved = unit.unsolved_cells()
            if len(unsolved) <= self.size:
                continue
            pool = [
                cell for cell in unsolved
                if 2 <= len(cell.candidates) <= self.size
            ]
            for combo in combinations(pool, self.size):
                digits: frozenset[int] = frozenset().union(
                    *(cell.candidates for cell in combo)
                )
                if len(digits) != self.size:
                    continue
                eliminations: list[tuple[int, int, int]] = []
                members = set(combo)
                for cell in unsolved:
                    if cell in members:
                        continue
                    for digit in sorted(digits & cell.candidates):
                        cell.remove_candidate(digit)
                        eliminations.append(
                            (cell.row_index, cell.column_index, digit)
                        )
                if eliminations:
                    digit_text = ", ".join(str(d) for d in sorted(digits))
                    cell_text = ", ".join(cell.label for cell in combo)
                    return Step(
                        technique=self.name,
                        description=(
                            f"naked {self.subset_word} {{{digit_text}}} in "
                            f"{cell_text} locks these digits inside "
                            f"{unit.name}"
                        ),
                        eliminations=tuple(eliminations),
                    )
        return None


class NakedPair(_NakedSubset):
    """Two cells of a house sharing the same two candidates."""

    name = "Naked Pair"
    size = 2
    subset_word = "pair"


class NakedTriple(_NakedSubset):
    """Three cells of a house whose candidates span three digits."""

    name = "Naked Triple"
    size = 3
    subset_word = "triple"


class NakedQuad(_NakedSubset):
    """Four cells of a house whose candidates span four digits."""

    name = "Naked Quad"
    size = 4
    subset_word = "quad"
