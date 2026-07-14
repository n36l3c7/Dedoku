"""Alternating Inference Chains (AIC) over candidate nodes.

Where X-Chains work on one digit and XY-Chains on bivalue cells, an AIC
walks the full candidate graph: nodes are ``(cell, digit)`` candidates.

* A **strong link** ("if false, then true") joins the two candidates of a
  bivalue cell, or the two homes of a conjugate pair.
* A **weak link** ("if true, then false") joins two candidates of the same
  cell, or two same-digit candidates sharing a house.

A chain with an odd number of links, starting and ending strongly, proves
that at least one endpoint is true: every candidate weakly linked to both
endpoints is eliminated. Chains are searched breadth-first, shortest
first. XY-Chains, X-Chains, and W-Wings are all special cases; the AIC is
kept last in the pipeline as the most general (and most expensive) rule.
"""

from __future__ import annotations

from collections import deque
from typing import TYPE_CHECKING, Iterator

from .base import Step, Technique

if TYPE_CHECKING:
    from ..cell import Cell
    from ..grid import Grid

__all__ = ["AIC"]

_MAX_LINKS = 12
"""int: Search depth cap; longer chains add cost, not coverage."""

_Node = tuple["Cell", int]


class AIC(Technique):
    """Eliminate through general alternating inference chains."""

    name = "AIC"

    def apply(self, grid: Grid) -> Step | None:
        """Find the shortest productive AIC on the board.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :returns: The eliminations performed, or ``None`` if no productive
            chain exists.
        :rtype: Step | None
        """
        strong = self._strong_links(grid)
        for cell in grid.cells:
            for digit in sorted(cell.candidates):
                origin = (cell, digit)
                if origin not in strong:
                    continue
                step = self._search(grid, origin, strong)
                if step is not None:
                    return step
        return None

    @staticmethod
    def _strong_links(grid: Grid) -> dict[_Node, list[_Node]]:
        """Build the strong-link adjacency of the candidate graph.

        :param grid: The board being searched.
        :type grid: Grid
        :returns: Adjacency between ``(cell, digit)`` nodes.
        :rtype: dict[tuple[Cell, int], list[tuple[Cell, int]]]
        """
        adjacency: dict[_Node, list[_Node]] = {}

        def link(one: _Node, two: _Node) -> None:
            adjacency.setdefault(one, []).append(two)
            adjacency.setdefault(two, []).append(one)

        for cell in grid.cells:
            if cell.is_bivalue:
                low, high = sorted(cell.candidates)
                link((cell, low), (cell, high))
        for unit in grid.units:
            for digit in sorted(unit.missing_values()):
                homes = unit.cells_with_candidate(digit)
                if len(homes) == 2:
                    link((homes[0], digit), (homes[1], digit))
        return adjacency

    @staticmethod
    def _weak_neighbours(node: _Node) -> Iterator[_Node]:
        """Yield every candidate a true ``node`` would switch off.

        :param node: The candidate assumed true.
        :type node: tuple[Cell, int]
        :returns: Candidates in the same cell or same-digit candidates in
            a shared house, in deterministic order.
        :rtype: Iterator[tuple[Cell, int]]
        """
        cell, digit = node
        for other_digit in sorted(cell.candidates - {digit}):
            yield (cell, other_digit)
        for peer in cell.peers:
            if digit in peer.candidates:
                yield (peer, digit)

    @staticmethod
    def _weakly_linked(one: _Node, two: _Node) -> bool:
        """Report whether two candidates cannot both be true.

        :param one: A candidate.
        :type one: tuple[Cell, int]
        :param two: Another candidate.
        :type two: tuple[Cell, int]
        :returns: ``True`` if the candidates share a cell or share a digit
            and a house.
        :rtype: bool
        """
        if one[0] is two[0]:
            return one[1] != two[1]
        return one[1] == two[1] and one[0].sees(two[0])

    def _search(
        self,
        grid: Grid,
        origin: _Node,
        strong: dict[_Node, list[_Node]],
    ) -> Step | None:
        """Breadth-first search of alternating chains from ``origin``.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :param origin: The chain's first candidate node.
        :type origin: tuple[Cell, int]
        :param strong: The strong-link adjacency.
        :type strong: dict
        :returns: The eliminations performed, or ``None``.
        :rtype: Step | None
        """
        first = (origin, 0)
        parent: dict[tuple[_Node, int], tuple[_Node, int] | None] = {
            first: None
        }
        queue: deque[tuple[_Node, int]] = deque([first])
        while queue:
            node, links = queue.popleft()
            if links >= _MAX_LINKS:
                continue
            if links % 2 == 0:
                nexts: Iterator[_Node] = iter(strong.get(node, ()))
            else:
                nexts = self._weak_neighbours(node)
            for nxt in nexts:
                state = (nxt, links + 1)
                if state in parent:
                    continue
                parent[state] = (node, links)
                if (links + 1) % 2 == 1 and links + 1 >= 3:
                    step = self._eliminate(grid, origin, nxt, parent, state)
                    if step is not None:
                        return step
                queue.append(state)
        return None

    def _eliminate(
        self,
        grid: Grid,
        origin: _Node,
        end: _Node,
        parent: dict,
        state: tuple[_Node, int],
    ) -> Step | None:
        """Apply the endpoint rule for one chain.

        :param grid: The board to inspect and mutate.
        :type grid: Grid
        :param origin: One chain endpoint.
        :type origin: tuple[Cell, int]
        :param end: The other chain endpoint.
        :type end: tuple[Cell, int]
        :param parent: BFS parent pointers used to rebuild the chain.
        :type parent: dict
        :param state: The end state to walk back from.
        :type state: tuple[tuple[Cell, int], int]
        :returns: The eliminations performed, or ``None`` if the chain
            removes nothing.
        :rtype: Step | None
        """
        chain: set[_Node] = set()
        cursor: tuple[_Node, int] | None = state
        while cursor is not None:
            chain.add(cursor[0])
            cursor = parent[cursor]
        eliminations: list[tuple[int, int, int]] = []
        for cell in grid.cells:
            for digit in sorted(cell.candidates):
                node = (cell, digit)
                if node in chain:
                    continue
                if self._weakly_linked(node, origin) and \
                        self._weakly_linked(node, end):
                    cell.remove_candidate(digit)
                    eliminations.append(
                        (cell.row_index, cell.column_index, digit)
                    )
        if not eliminations:
            return None
        return Step(
            technique=self.name,
            description=(
                f"AIC of {state[1]} links from digit {origin[1]} at "
                f"{origin[0].label} to digit {end[1]} at {end[0].label}: "
                f"one endpoint is true, so every candidate weakly linked "
                f"to both is removed"
            ),
            eliminations=tuple(eliminations),
        )
