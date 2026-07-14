"""Logical solving techniques, ordered from simplest to most advanced.

Each technique is a stateless :class:`~sudoku_solver.techniques.base.Technique`
subclass. The default pipeline used by
:class:`~sudoku_solver.solver.SudokuSolver` instantiates them in difficulty
order; further strategies (intersection removal, X-Wing, colouring, wings,
uniqueness arguments, ...) will extend this package.
"""

from __future__ import annotations

from .base import Step, Technique
from .bug import BivalueUniversalGrave
from .chute import ChuteRemotePairs
from .colouring import SimpleColouring
from .fish import Swordfish, XWing
from .hidden import HiddenPair, HiddenQuad, HiddenSingle, HiddenTriple
from .intersections import ClaimingCandidates, PointingCandidates
from .naked import NakedPair, NakedQuad, NakedSingle, NakedTriple
from .rectangles import UniqueRectangle
from .wings import XYZWing, YWing
from .wwing import WWing

__all__ = [
    "Step",
    "Technique",
    "NakedSingle",
    "NakedPair",
    "NakedTriple",
    "NakedQuad",
    "HiddenSingle",
    "HiddenPair",
    "HiddenTriple",
    "HiddenQuad",
    "PointingCandidates",
    "ClaimingCandidates",
    "XWing",
    "ChuteRemotePairs",
    "SimpleColouring",
    "WWing",
    "YWing",
    "UniqueRectangle",
    "Swordfish",
    "XYZWing",
    "BivalueUniversalGrave",
]
