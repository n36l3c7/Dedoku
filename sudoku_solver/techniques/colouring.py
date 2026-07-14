"""Simple Colouring (single-digit chains) technique.

For one digit, a *conjugate link* connects the two cells of a house that
are its only remaining homes there: exactly one of them must hold the
digit. Following such links builds chains whose cells can be split into
two alternating colours — one colour is entirely true, the other entirely
false.

Two classic deductions follow:

* **Colour wrap** — if two cells of the same colour see each other, that
  colour is false, and the digit is removed from every cell of it.
* **Colour trap** — if an uncoloured cell sees both colours, one of the two
  colours must be true, so the cell can never hold the digit.
"""

from __future__ import annotations

from itertools import combinations
from typing import TYPE_CHECKING

from ..exceptions import ContradictionError
from .base import Step, Technique

if TYPE_CHECKING:
    from ..cell import Cell
    from ..grid import Grid

__all__ = ["SimpleColouring"]


def _sees(first: Cell, second: Cell) -> bool:
    """Report whether two distinct cells share a house.

    :param first: One cell.
    :type first: Cell
    :param second: Another cell.
    :type second: Cell
    :returns: ``True`` if the cells share a row, column, or subgrid.
    :rtype: bool
    """
    return (
        first.row_index == second.row_index
        or first.column_index == second.column_index
        or first.subgrid.index == second.subgrid.index
    )


class SimpleColouring(Technique):
    """Eliminate a digit through two-colour conjugate chains."""

    name = "Simple Colouring"

    def apply(self, grid: Grid) -> Step | None:
        """Find the first productive colour wrap or colour trap.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The eliminations performed, or ``None`` if no chain
            yields a deduction.
        :rtype: Step | None
        :raises ContradictionError: If a chain contains an odd conjugate
            cycle, which proves the board inconsistent.
        """
        for digit in range(1, 10):
            adjacency = self._conjugate_links(grid, digit)
            visited: set[Cell] = set()
            for start in grid.cells:
                if start not in adjacency or start in visited:
                    continue
                colours = self._colour_component(start, adjacency, digit)
                visited.update(colours)
                step = self._colour_wrap(digit, colours)
                if step is None:
                    step = self._colour_trap(grid, digit, colours)
                if step is not None:
                    return step
        return None

    @staticmethod
    def _conjugate_links(grid: Grid, digit: int) -> dict[Cell, list[Cell]]:
        """Build the conjugate-link graph of ``digit`` over the board.

        :param grid: The board being searched.
        :type grid: Grid
        :param digit: The digit to build the graph for.
        :type digit: int
        :returns: An adjacency mapping between conjugate-linked cells.
        :rtype: dict[Cell, list[Cell]]
        """
        adjacency: dict[Cell, list[Cell]] = {}
        for unit in grid.units:
            homes = unit.cells_with_candidate(digit)
            if len(homes) == 2:
                first, second = homes
                adjacency.setdefault(first, []).append(second)
                adjacency.setdefault(second, []).append(first)
        return adjacency

    @staticmethod
    def _colour_component(
        start: Cell, adjacency: dict[Cell, list[Cell]], digit: int
    ) -> dict[Cell, int]:
        """Two-colour the chain component containing ``start``.

        :param start: Any cell of the component.
        :type start: Cell
        :param adjacency: The conjugate-link graph.
        :type adjacency: dict[Cell, list[Cell]]
        :param digit: The digit the chain is built on (for error messages).
        :type digit: int
        :returns: A mapping from each component cell to colour 0 or 1.
        :rtype: dict[Cell, int]
        :raises ContradictionError: If the component contains an odd cycle.
        """
        colours: dict[Cell, int] = {start: 0}
        queue: list[Cell] = [start]
        while queue:
            current = queue.pop(0)
            for neighbour in adjacency[current]:
                if neighbour not in colours:
                    colours[neighbour] = 1 - colours[current]
                    queue.append(neighbour)
                elif colours[neighbour] == colours[current]:
                    raise ContradictionError(
                        f"odd conjugate cycle on digit {digit} around "
                        f"{neighbour.label}"
                    )
        return colours

    def _colour_wrap(
        self, digit: int, colours: dict[Cell, int]
    ) -> Step | None:
        """Apply the colour-wrap rule to one coloured component.

        :param digit: The digit the chain is built on.
        :type digit: int
        :param colours: The two-colouring of the component.
        :type colours: dict[Cell, int]
        :returns: The eliminations performed, or ``None``.
        :rtype: Step | None
        """
        for false_colour in (0, 1):
            group = sorted(
                (cell for cell, colour in colours.items()
                 if colour == false_colour),
                key=lambda cell: cell.position,
            )
            witness = next(
                (
                    (first, second)
                    for first, second in combinations(group, 2)
                    if _sees(first, second)
                ),
                None,
            )
            if witness is None:
                continue
            eliminations: list[tuple[int, int, int]] = []
            for cell in group:
                if cell.remove_candidate(digit):
                    eliminations.append(
                        (cell.row_index, cell.column_index, digit)
                    )
            return Step(
                technique=self.name,
                description=(
                    f"colouring digit {digit}: {witness[0].label} and "
                    f"{witness[1].label} share the same colour and see "
                    f"each other, so that whole colour is false"
                ),
                eliminations=tuple(eliminations),
            )
        return None

    def _colour_trap(
        self, grid: Grid, digit: int, colours: dict[Cell, int]
    ) -> Step | None:
        """Apply the colour-trap rule to one coloured component.

        :param grid: The board being searched.
        :type grid: Grid
        :param digit: The digit the chain is built on.
        :type digit: int
        :param colours: The two-colouring of the component.
        :type colours: dict[Cell, int]
        :returns: The eliminations performed, or ``None``.
        :rtype: Step | None
        """
        group_zero = [cell for cell, colour in colours.items() if colour == 0]
        group_one = [cell for cell, colour in colours.items() if colour == 1]
        eliminations: list[tuple[int, int, int]] = []
        trapped_labels: list[str] = []
        for cell in grid.cells:
            if cell in colours or digit not in cell.candidates:
                continue
            if any(_sees(cell, other) for other in group_zero) and any(
                _sees(cell, other) for other in group_one
            ):
                cell.remove_candidate(digit)
                eliminations.append(
                    (cell.row_index, cell.column_index, digit)
                )
                trapped_labels.append(cell.label)
        if not eliminations:
            return None
        return Step(
            technique=self.name,
            description=(
                f"colouring digit {digit}: {', '.join(trapped_labels)} "
                f"see(s) both colours of the chain, so the digit is "
                f"removed there"
            ),
            eliminations=tuple(eliminations),
        )
