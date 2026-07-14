Usage
=====

Solving a puzzle
----------------

The quickest path is the one-liner:

.. code-block:: python

   import dedoku

   result = dedoku.solve(puzzle)          # puzzle: 81-character string
   result.solved                          # True when fully solved
   result.grid                            # the final Grid (or partial board)
   result.steps                           # every deduction, in order
   result.techniques_used                 # distinct techniques, first-use order

Puzzle strings are 81 characters, read left to right, top to bottom:
digits ``1``–``9`` are givens, ``0`` or ``.`` mark empty cells; whitespace
and the decoration characters ``|``, ``-``, ``+`` are ignored, so
pretty-printed boards parse back.

For full control, work with the board and solver directly:

.. code-block:: python

   from dedoku import Grid, SudokuSolver

   grid = Grid.from_string(puzzle)
   result = SudokuSolver().solve(grid)    # mutates and returns the grid

Reading the solving path
------------------------

Each :class:`~dedoku.Step` records the technique, a human-readable
description, and the exact effect on the board:

.. code-block:: python

   for step in result.steps:
       for placement in step.placements:
           print(f"{step.technique}: R{placement.row + 1}"
                 f"C{placement.column + 1} = {placement.digit}")
       for elimination in step.eliminations:
           print(f"{step.technique}: {elimination.digit} removed from "
                 f"R{elimination.row + 1}C{elimination.column + 1}")

When you just need the answer
-----------------------------

By default dedoku never guesses. For the rare puzzles beyond the logical
pipeline — or when explainability does not matter — opt in explicitly:

.. code-block:: python

   dedoku.solve(puzzle, method="hybrid")         # logic first, then brute force
   dedoku.solve(puzzle, method="backtracking")   # brute force directly

Anything brute-forced is recorded as an explicit ``"Backtracking"`` step,
and ``result.used_backtracking`` reports whether it ran — the solving path
never lies about how a cell was filled. In hybrid mode the search runs on
the candidates the techniques already narrowed, so the brute-force tail is
typically tiny. On puzzles that may have multiple solutions, combine
``method="hybrid"`` with ``assume_unique=False``.

Puzzles without a guaranteed unique solution
--------------------------------------------

Four techniques (unique rectangles types 1 and 2, BUG, avoidable
rectangles) are only sound when the puzzle has exactly one solution — the
convention for published Sudokus. When that is not guaranteed, exclude
them:

.. code-block:: python

   result = dedoku.solve(puzzle, assume_unique=False)

Custom pipelines
----------------

Pass any sequence of techniques, tried in order with a restart after
every successful deduction:

.. code-block:: python

   from dedoku import SudokuSolver
   from dedoku.techniques import HiddenSingle, NakedSingle, XYChain

   solver = SudokuSolver(techniques=[NakedSingle(), HiddenSingle(), XYChain()])

The board model is fully navigable for writing your own techniques: each
:class:`~dedoku.Cell` knows its ``row``, ``column``, ``subgrid``,
``candidates``, and ``peers``; the :class:`~dedoku.Grid` exposes all 27
houses via ``rows``, ``columns``, ``subgrids``, and ``units``.
