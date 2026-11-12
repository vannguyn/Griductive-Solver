"""Public engine port protocol consumed by the deductive agent."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState, VerdictOutcome
from griductive.domain.types import Status


@runtime_checkable
class PublicGame(Protocol):
    """Restricted public interface exposed to agents (no hidden solution access)."""

    def public_state(self) -> PublicState:
        """Return the current sanitized `PublicState` snapshot."""
        ...

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Submit a deduced verdict for `cell` and return the `VerdictOutcome`."""
        ...
