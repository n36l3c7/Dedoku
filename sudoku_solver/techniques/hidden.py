"""Hidden candidate techniques: Single, Pair, Triple, and Quad.

A *hidden* subset is a group of ``n`` digits whose candidate homes inside
one house are confined to the same ``n`` cells. Those cells must receive
those digits, so every other candidate can be stripped from them. With
``n = 1`` the digit has a single home and is placed directly.
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from ..exceptions import ContradictionError
from .base import Step, Technique

if TYPE_CHECKING:
    from ..grid import Grid

__all__ = ["HiddenSingle", "HiddenPair", "HiddenTriple", "HiddenQuad"]


class HiddenSingle(Technique):
    """Place any digit that has a single possible home inside a house."""

    name = "Hidden Single"

    def apply(self, grid: Grid) -> Step | None:
        """Find the first digit confined to one cell of a house and place it.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The placement performed, or ``None`` if every missing
            digit still has two or more homes in each house.
        :rtype: Step | None
        :raises ContradictionError: If a missing digit has no home left
            inside a house, which proves the board inconsistent.
        """
        for unit in grid.units:
            for digit in sorted(unit.missing_values()):
                homes = unit.cells_with_candidate(digit)
                if not homes:
                    raise ContradictionError(
                        f"digit {digit} has no available cell in {unit.name}"
                    )
                if len(homes) == 1:
                    cell = homes[0]
                    cell.set_value(digit)
                    return Step(
                        technique=self.name,
                        description=(
                            f"in {unit.name}, digit {digit} fits only "
                            f"in {cell.label}"
                        ),
                        placements=(
                            (cell.row_index, cell.column_index, digit),
                        ),
                    )
        return None


class _HiddenSubset(Technique):
    """Shared implementation for hidden pairs, triples, and quads.

    :cvar size: Number of digits (and cells) forming the subset.
    :cvar subset_word: Human-readable subset name used in descriptions.
    """

    size: int = 0
    subset_word: str = ""

    def apply(self, grid: Grid) -> Step | None:
        """Find the first hidden subset that eliminates at least one candidate.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The eliminations performed, or ``None`` if no productive
            hidden subset of this size exists.
        :rtype: Step | None
        """
        for unit in grid.units:
            missing = sorted(unit.missing_values())
            if len(missing) <= self.size:
                continue
            unsolved = unit.unsolved_cells()
            for digits in combinations(missing, self.size):
                digit_set = frozenset(digits)
                homes = [
                    cell for cell in unsolved
                    if cell.candidates & digit_set
                ]
                if len(homes) != self.size:
                    continue
                if not all(
                    any(digit in cell.candidates for cell in homes)
                    for digit in digit_set
                ):
                    continue
                eliminations: list[tuple[int, int, int]] = []
                for cell in homes:
                    for digit in sorted(cell.candidates - digit_set):
                        cell.remove_candidate(digit)
                        eliminations.append(
                            (cell.row_index, cell.column_index, digit)
                        )
                if eliminations:
                    digit_text = ", ".join(str(d) for d in sorted(digit_set))
                    cell_text = ", ".join(cell.label for cell in homes)
                    return Step(
                        technique=self.name,
                        description=(
                            f"hidden {self.subset_word} {{{digit_text}}} in "
                            f"{unit.name} confines these digits to "
                            f"{cell_text}"
                        ),
                        eliminations=tuple(eliminations),
                    )
        return None


class HiddenPair(_HiddenSubset):
    """Two digits confined to the same two cells of a house."""

    name = "Hidden Pair"
    size = 2
    subset_word = "pair"


class HiddenTriple(_HiddenSubset):
    """Three digits confined to the same three cells of a house."""

    name = "Hidden Triple"
    size = 3
    subset_word = "triple"


class HiddenQuad(_HiddenSubset):
    """Four digits confined to the same four cells of a house."""

    name = "Hidden Quad"
    size = 4
    subset_word = "quad"
