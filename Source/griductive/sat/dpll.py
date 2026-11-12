"""DPLL solver with propagation, branching, and backtracking."""

from __future__ import annotations

from collections.abc import Sequence

from griductive.sat.cnf import CNF, Literal, SatResult


class DPLLSolver:
    """Pure DPLL SAT solver operating on integer CNF formulas."""

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[Literal] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Solve `cnf` with optional unit `assumptions` and monotonic `deadline`."""
        raise NotImplementedError
