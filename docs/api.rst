API reference
=============

Top level
---------

.. autofunction:: dedoku.solve

The board
---------

.. autoclass:: dedoku.Grid
   :members:

.. autoclass:: dedoku.Cell
   :members:

.. autodata:: dedoku.DIGITS

Houses
------

.. autoclass:: dedoku.Unit
   :members:

.. autoclass:: dedoku.Row
   :members:

.. autoclass:: dedoku.Column
   :members:

.. autoclass:: dedoku.Subgrid
   :members:

The solver
----------

.. autoclass:: dedoku.SudokuSolver
   :members:

.. autoclass:: dedoku.SolveResult
   :members:

.. autoclass:: dedoku.Step
   :members:

.. autoclass:: dedoku.Placement
   :members:

.. autoclass:: dedoku.Elimination
   :members:

.. autoclass:: dedoku.Technique
   :members:

Brute force (opt-in)
--------------------

.. automodule:: dedoku.backtracking
   :members:

Exceptions
----------

.. automodule:: dedoku.exceptions
   :members:

Command-line module
-------------------

.. automodule:: dedoku.cli
   :members:
