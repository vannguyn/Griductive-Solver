"""Reasoning trace and reveal-wave records."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.grid import Coord
from griductive.domain.types import Classification, SolveStatus, Status, VerdictResult
from griductive.sat.cnf import SatStatus


@dataclass(frozen=True)
class TraceSatQuery:
    """Human- and report-friendly record of a single SAT entailment query."""

    coord: Coord
    assumed_status: Status
    status: SatStatus


@dataclass(frozen=True)
class TraceStep:
    """Single accepted/attempted deduction step within an auto-solve trace (PDF §4.4)."""

    step: int
    wave: int
    cell: Coord
    classification: Classification
    active_clue_ids: tuple[str, ...]
    sat_queries: tuple[TraceSatQuery, ...]
    verdict_result: VerdictResult
    revealed_clue_id: str | None
    runtime_ms: float


@dataclass(frozen=True)
class SolveTrace:
    """Complete execution trace and aggregated metrics for an auto-solve run."""

    puzzle_id: str
    status: SolveStatus
    steps: tuple[TraceStep, ...]
    reveal_waves: int
    total_sat_calls: int
    total_decisions: int
    total_propagations: int
    total_backtracks: int
    total_runtime_ms: float
