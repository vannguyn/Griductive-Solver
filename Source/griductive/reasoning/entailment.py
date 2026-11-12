"""Classify a cell by SAT entailment."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.types import Classification
from griductive.sat.cnf import CNF, SatStatus
from griductive.sat.solver import SatSolver


@dataclass(frozen=True)
class SatQuery:
    """Single SAT query issued during entailment checking."""

    var_id: int
    assumed_literal: int
    status: SatStatus


@dataclass(frozen=True)
class ClassifyOutcome:
    """Entailment classification together with all SAT queries executed."""

    classification: Classification
    queries: tuple[SatQuery, ...]


def check_kb_consistent(
    cnf_kb: CNF,
    solver: SatSolver,
    deadline: float | None = None,
) -> SatStatus:
    """Check once per reveal wave whether `cnf_kb` itself is SAT, UNSAT, or TIMEOUT."""
    raise NotImplementedError


def classify(
    cnf_kb: CNF,
    var_id: int,
    solver: SatSolver,
    deadline: float | None = None,
) -> ClassifyOutcome:
    """Classify primary variable `var_id` via two-query SAT entailment (PDF §3.4)."""
    raise NotImplementedError
