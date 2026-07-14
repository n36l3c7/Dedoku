"""Chute Remote Pairs technique.

A *chute* is a band (three stacked rows covering three subgrids) or a
stack (three adjacent columns covering three subgrids). Take two bivalue
cells with the same candidate pair ``{a, b}`` inside one chute, lying in
different subgrids and different lines, so they share no house. Exactly
three chute cells see neither of them: the intersection of the remaining
line and the remaining subgrid.

If digit ``a`` can appear in none of those three cells (neither as a value
nor as a candidate), the two pair cells cannot both hold ``a`` — otherwise
the remaining subgrid would have no home for ``a`` at all. Hence at least
one pair cell holds ``b``, and ``b`` can be eliminated from every cell that
sees both pair cells.
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from .base import Step, Technique

if TYPE_CHECKING:
    from ..cell import Cell
    from ..grid import Grid

__all__ = ["ChuteRemotePairs"]


class ChuteRemotePairs(Technique):
    """Eliminate via two same-pair bivalue cells spread across a chute."""

    name = "Chute Remote Pairs"

    def apply(self, grid: Grid) -> Step | None:
        """Find the first productive chute remote pair on the board.

        Bands (horizontal chutes) are searched before stacks.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The eliminations performed, or ``None`` if no productive
            pattern exists.
        :rtype: Step | None
        """
        for is_band in (True, False):
            for chute_index in range(3):
                step = self._search_chute(grid, chute_index, is_band)
                if step is not None:
                    return step
        return None

    def _search_chute(
        self, grid: Grid, chute_index: int, is_band: bool
    ) -> Step | None:
        """Search a single chute for a productive remote pair.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :param chute_index: Zero-based index of the chute (0-2).
        :type chute_index: int
        :param is_band: ``True`` for a band of rows, ``False`` for a stack
            of columns.
        :type is_band: bool
        :returns: The eliminations performed, or ``None``.
        :rtype: Step | None
        """
        lines = grid.rows if is_band else grid.columns
        line_indices = range(3 * chute_index, 3 * chute_index + 3)
        chute_lines = [lines[index] for index in line_indices]
        bivalues = [
            cell
            for line in chute_lines
            for cell in line
            if cell.is_bivalue
        ]

        def line_of(cell: Cell) -> int:
            return cell.row_index if is_band else cell.column_index

        chute_name = f"{'band' if is_band else 'stack'} {chute_index + 1}"
        for first, second in combinations(bivalues, 2):
            if first.candidates != second.candidates:
                continue
            if first.subgrid is second.subgrid:
                continue
            if line_of(first) == line_of(second):
                continue
            blind = self._blind_cells(grid, first, second, line_indices, is_band)
            pair = sorted(first.candidates)
            for absent, present in (tuple(pair), tuple(reversed(pair))):
                if any(
                    cell.value == absent or absent in cell.candidates
                    for cell in blind
                ):
                    continue
                eliminations: list[tuple[int, int, int]] = []
                common = set(first.peers) & set(second.peers)
                for cell in sorted(common, key=lambda c: c.position):
                    if cell.remove_candidate(present):
                        eliminations.append(
                            (cell.row_index, cell.column_index, present)
                        )
                if eliminations:
                    pair_text = ", ".join(str(d) for d in pair)
                    return Step(
                        technique=self.name,
                        description=(
                            f"remote pair {{{pair_text}}} at {first.label} "
                            f"and {second.label} in {chute_name}: digit "
                            f"{absent} cannot occupy the chute cells seeing "
                            f"neither of them, so digit {present} is removed "
                            f"from every cell seeing both"
                        ),
                        eliminations=tuple(eliminations),
                    )
        return None

    @staticmethod
    def _blind_cells(
        grid: Grid,
        first: Cell,
        second: Cell,
        line_indices: range,
        is_band: bool,
    ) -> tuple[Cell, ...]:
        """Return the three chute cells that see neither pair cell.

        They form the intersection of the chute line and the chute subgrid
        containing neither pair cell.

        :param grid: The board being searched.
        :type grid: Grid
        :param first: One remote-pair cell.
        :type first: Cell
        :param second: The other remote-pair cell.
        :type second: Cell
        :param line_indices: The three line indices spanning the chute.
        :type line_indices: range
        :param is_band: ``True`` for a band of rows, ``False`` for a stack.
        :type is_band: bool
        :returns: The three cells seeing neither pair cell.
        :rtype: tuple[Cell, ...]
        """
        if is_band:
            used_lines = {first.row_index, second.row_index}
        else:
            used_lines = {first.column_index, second.column_index}
        remaining_line = next(
            index for index in line_indices if index not in used_lines
        )
        used_boxes = {first.subgrid.index, second.subgrid.index}
        remaining_box = next(
            subgrid
            for subgrid in grid.subgrids
            if subgrid.index not in used_boxes
            and any(
                (cell.row_index if is_band else cell.column_index)
                in line_indices
                for cell in subgrid
            )
        )
        return tuple(
            cell
            for cell in remaining_box
            if (cell.row_index if is_band else cell.column_index)
            == remaining_line
        )
