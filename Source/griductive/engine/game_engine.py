"""Game-loop operations: verdict, reveal, restart, and public state."""

from __future__ import annotations

from typing import Any

from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState, VerdictOutcome
from griductive.domain.types import Status
from griductive.sat.solver import SatSolver


class GameEngine:
    """Stateful game engine enforcing public reasoning before revealing cells or clues."""

    def __init__(self, puzzle: Any, solver: SatSolver | None = None) -> None:
        """Initialize engine state at $KB_0$ (`initially_revealed`) for `puzzle`."""
        raise NotImplementedError

    def public_state(self) -> PublicState:
        """Return the current sanitized `PublicState` (satisfying `PublicGame`)."""
        raise NotImplementedError

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Validate `cell` against `PublicKnowledge` and reveal clue only if ACCEPTED."""
        raise NotImplementedError

    def restart(self) -> PublicState:
        """Reset game state back to initial $KB_0$ (`initially_revealed`) for the puzzle."""
        raise NotImplementedError
