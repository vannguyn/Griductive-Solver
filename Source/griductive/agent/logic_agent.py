"""Deductive agent that consumes public state only."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass

from griductive.agent.ports import PublicGame
from griductive.agent.trace import SolveTrace, TraceStep
from griductive.domain.public_state import PublicState
from griductive.sat.solver import CountingSolver, SatSolver


@dataclass(frozen=True)
class AutoSolveStep:
    """Incremental event yielded per auto-solve step or terminal status transition."""

    step: TraceStep | None
    public_state: PublicState
    trace: SolveTrace


class LogicAgent:
    """Iterative deductive solver interacting strictly through `PublicGame`."""

    solver: CountingSolver

    def __init__(self, solver: SatSolver) -> None:
        """Initialize the agent, wrapping `solver` in `CountingSolver` if not already wrapped."""
        raise NotImplementedError

    def iter_steps(
        self,
        game: PublicGame,
        deadline: float | None = None,
    ) -> Iterator[AutoSolveStep]:
        """Yield `AutoSolveStep` events incrementally across reveal waves until done."""
        raise NotImplementedError

    def run(
        self,
        game: PublicGame,
        deadline: float | None = None,
    ) -> SolveTrace:
        """Consume `iter_steps` to completion and return the final `SolveTrace`."""
        raise NotImplementedError
