"""CNF, clause, literal, and DIMACS representations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from griductive.sat.stats import SolverStats

Literal = int
Clause = list[int]


class SatStatus(str, Enum):
    """Outcome status of a pure SAT solver call."""

    SAT = "SAT"
    UNSAT = "UNSAT"
    TIMEOUT = "TIMEOUT"


@dataclass
class CNF:
    """Integer CNF formula in 1-based variable indexing (`1..num_vars`)."""

    num_vars: int
    clauses: list[Clause]

    def to_dimacs(self) -> str:
        """Serialize this CNF formula to DIMACS CNF format."""
        raise NotImplementedError


@dataclass(frozen=True)
class SatResult:
    """Result of solving a CNF formula under optional unit assumptions."""

    status: SatStatus
    model: dict[int, bool] | None
    stats: SolverStats
