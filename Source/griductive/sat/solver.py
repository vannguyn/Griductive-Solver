"""Abstract SAT solver protocol and counting wrapper."""

from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol, runtime_checkable

from griductive.sat.cnf import CNF, Literal, SatResult


@runtime_checkable
class SatSolver(Protocol):
    """Protocol implemented by SAT solver backends and wrappers."""

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[Literal] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Solve `cnf` under unit `assumptions` respecting optional monotonic `deadline`."""
        ...


class CountingSolver:
    """SatSolver wrapper accumulating call counts and cumulative DPLL stats."""

    inner: SatSolver
    calls: int
    total_decisions: int
    total_propagations: int
    total_backtracks: int
    total_runtime_ms: float

    def __init__(self, inner: SatSolver) -> None:
        """Initialize wrapper counters around an underlying `SatSolver`."""
        raise NotImplementedError

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[Literal] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Delegate solving to `inner` and accumulate call count and solver stats."""
        raise NotImplementedError

    def reset_stats(self) -> None:
        """Reset all accumulated counters and runtime metrics to zero."""
        raise NotImplementedError
