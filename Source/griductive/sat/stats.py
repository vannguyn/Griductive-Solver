"""DPLL performance counters."""

from dataclasses import dataclass


@dataclass
class SolverStats:
    """Cumulative statistics recorded during SAT solving."""

    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime_ms: float = 0.0
