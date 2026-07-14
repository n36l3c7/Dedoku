Command line
============

Installing the package also installs the ``dedoku`` command
(equivalently: ``python -m dedoku``).

.. code-block:: bash

   dedoku 530070000600195000098000060800060003400803001700020006060000280000419005000080079

prints the solved board and a summary. Add ``--explain`` to watch the
whole reasoning, cell by cell:

.. code-block:: text

      1. R5C5 = 5               [Naked Single] R5C5 has 5 as its only candidate
      2. R5C2 = 2               [Naked Single] R5C2 has 2 as its only candidate
      ...
     51. R9C3 = 5               [Naked Single] R9C3 has 5 as its only candidate

   5 3 4 | 6 7 8 | 9 1 2
   6 7 2 | 1 9 5 | 3 4 8
   ...

   Solved in 51 steps using: Naked Single

Options
-------

``puzzle``
    The 81-character puzzle. When omitted, the puzzle is read from
    standard input, so ``cat puzzle.txt | dedoku -e`` works too.

``-e, --explain``
    Print every deduction in order before the final board: placements as
    ``RxCy = digit``, eliminations as a removal count, each with the
    technique name and its explanation.

``--method {logic,hybrid,backtracking}``
    ``logic`` (default) uses the explainable techniques only and may
    stall on the hardest puzzles; ``hybrid`` completes any remainder by
    brute force; ``backtracking`` brute-forces directly. Brute-forced
    cells appear in ``--explain`` as one explicit ``[Backtracking]``
    step.

``--multi``
    Do not assume the puzzle has a unique solution (disables the
    uniqueness-based techniques).

``--version``
    Print the installed version and exit.

Exit codes
----------

========  =====================================================
``0``     The puzzle was completely solved.
``1``     Pure logic stalled; the partial board is printed.
``2``     The input was malformed or self-contradictory.
========  =====================================================
