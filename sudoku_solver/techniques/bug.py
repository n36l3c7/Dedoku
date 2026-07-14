"""Bivalue Universal Grave (BUG) technique, in its BUG+1 form.

A *bivalue universal grave* is a board state where every unsolved cell has
exactly two candidates and every candidate appears exactly twice in each
house. Such a state can never belong to a puzzle with a unique solution:
the remaining digits could be assigned in two complementary ways.

The practical *BUG+1* deduction: when every unsolved cell is bivalue
except a single cell with three candidates, that cell must take the one
candidate appearing three times in its row, column, and subgrid — placing
any other value would leave the board as a deadly BUG. Like the other
uniqueness arguments, this assumes the puzzle has exactly one solution.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import Step, Technique

if TYPE_CHECKING:
    from ..grid import Grid

__all__ = ["BivalueUniversalGrave"]


class BivalueUniversalGrave(Technique):
    """Resolve a BUG+1 state by solving its only trivalue cell."""

    name = "BUG"

    def apply(self, grid: Grid) -> Step | None:
        """Detect a BUG+1 state and place the BUG-breaking digit.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The placement performed, or ``None`` if the board is not
            in a BUG+1 state.
        :rtype: Step | None
        """
        trivalue = None
        for cell in grid.cells:
            if cell.is_solved:
                continue
            size = len(cell.candidates)
            if size == 2:
                continue
            if size == 3 and trivalue is None:
                trivalue = cell
                continue
            return None
        if trivalue is None:
            return None
        for digit in sorted(trivalue.candidates):
            counts = [
                len(unit.cells_with_candidate(digit))
                for unit in (trivalue.row, trivalue.column, trivalue.subgrid)
            ]
            if all(count == 3 for count in counts):
                trivalue.set_value(digit)
                return Step(
                    technique=self.name,
                    description=(
                        f"BUG+1: every unsolved cell is bivalue except "
                        f"{trivalue.label}; only digit {digit} appears "
                        f"three times in its houses, so it must go there "
                        f"to avoid a deadly bivalue universal grave"
                    ),
                    placements=(
                        (trivalue.row_index, trivalue.column_index, digit),
                    ),
                )
        return None
