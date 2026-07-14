"""Opt-in brute-force completion.

Backtracking is **not** a logical technique, and this module is
deliberately kept outside :mod:`dedoku.techniques`: the default pipeline
never touches it. It exists for the explicit ``hybrid`` and
``backtracking`` solving modes, where the caller chooses to trade
explainability for a guaranteed answer.

The search runs over the grid's *current candidates*, so every candidate
already removed by sound logic narrows it — in hybrid mode the brute-force
tail is typically tiny.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .grid import Grid

__all__ = ["complete_with_backtracking"]


def complete_with_backtracking(grid: Grid) -> bool:
    """Complete ``grid`` by depth-first search over its candidates.

    Solved cells are taken as fixed; unsolved cells only try digits still
    among their candidates. On success the found values are placed on the
    grid (with normal propagation); on failure the grid is left untouched.

    :param grid: The board to complete in place.
    :type grid: Grid
    :returns: ``True`` when a completion was found and applied, ``False``
        when no completion exists for the current board state.
    :rtype: bool
    """
    unsolved = [cell for cell in grid.cells if not cell.is_solved]
    if not unsolved:
        return grid.is_valid()

    rows = [0] * 9
    cols = [0] * 9
    boxes = [0] * 9
    for cell in grid.cells:
        if cell.value is not None:
            bit = 1 << cell.value
            rows[cell.row_index] |= bit
            cols[cell.column_index] |= bit
            boxes[cell.subgrid.index] |= bit

    allowed = {
        cell: sum(1 << digit for digit in cell.candidates)
        for cell in unsolved
    }
    values: dict = {}

    def recurse(remaining: list) -> bool:
        if not remaining:
            return True
        # Most-constrained cell first keeps the search shallow.
        best_index = -1
        best_options = 10
        for index, cell in enumerate(remaining):
            used = (rows[cell.row_index] | cols[cell.column_index]
                    | boxes[cell.subgrid.index])
            options = bin(allowed[cell] & ~used).count("1")
            if options < best_options:
                best_options, best_index = options, index
                if options <= 1:
                    break
        if best_options == 0:
            return False
        cell = remaining[best_index]
        rest = remaining[:best_index] + remaining[best_index + 1:]
        used = (rows[cell.row_index] | cols[cell.column_index]
                | boxes[cell.subgrid.index])
        mask = allowed[cell] & ~used
        for digit in range(1, 10):
            bit = 1 << digit
            if not mask & bit:
                continue
            rows[cell.row_index] |= bit
            cols[cell.column_index] |= bit
            boxes[cell.subgrid.index] |= bit
            values[cell] = digit
            if recurse(rest):
                return True
            del values[cell]
            rows[cell.row_index] ^= bit
            cols[cell.column_index] ^= bit
            boxes[cell.subgrid.index] ^= bit
        return False

    if not recurse(unsolved):
        return False
    for cell in unsolved:
        if not cell.is_solved:  # propagation may have solved it already
            cell.set_value(values[cell])
    return True
