"""Thin application facade mediating PyQt6 GUI, GameEngine, and LogicAgent."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from griductive.agent.hint import Hint
from griductive.agent.logic_agent import AutoSolveStep
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState, VerdictOutcome
from griductive.domain.types import Status


class GameSession:
    """Single-owner application session facade used by the desktop PyQt6 UI."""

    def load_puzzle(self, path: str | Path) -> PublicState:
        """Load a puzzle file into `GameEngine` and return the initial `PublicState`."""
        raise NotImplementedError

    def restart(self) -> PublicState:
        """Restart the active puzzle back to its initial $KB_0$ state."""
        raise NotImplementedError

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Forward a manual verdict to `GameEngine` and return the `VerdictOutcome`."""
        raise NotImplementedError

    def hint(self) -> Hint | None:
        """Request a safe deductive hint from current `PublicKnowledge`."""
        raise NotImplementedError

    def auto_solve_steps(
        self,
        timeout_ms: int | None = None,
    ) -> Iterator[AutoSolveStep]:
        """Run `LogicAgent.iter_steps` with optional timeout and yield `AutoSolveStep`."""
        raise NotImplementedError
