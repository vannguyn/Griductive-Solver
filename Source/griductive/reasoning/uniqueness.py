"""Puzzle uniqueness checking using a blocking clause."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.types import UniquenessResult
from griductive.sat.cnf import CNF
from griductive.sat.solver import SatSolver
from griductive.sat.stats import SolverStats


@dataclass(frozen=True)
class UniquenessOutput:
    """Result of checking whether a puzzle has a unique primary-variable solution."""

    result: UniquenessResult
    first_model: dict[int, bool] | None
    stats: SolverStats


def check_uniqueness(
    cnf: CNF,
    num_primary_vars: int,
    solver: SatSolver,
    deadline: float | None = None,
) -> UniquenessOutput:
    """Check UNIQUE / MULTIPLE / UNSAT / TIMEOUT by blocking only `1..num_primary_vars`."""
    raise NotImplementedError
