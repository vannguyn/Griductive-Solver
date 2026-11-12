"""PublicKnowledge model containing revealed clues and proved verdicts."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from griductive.domain.clue import Clue
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState
from griductive.domain.types import Status


@dataclass(frozen=True)
class PublicKnowledge:
    """Publicly known facts extracted from revealed cards and unlocked clues."""

    size: int
    revealed_clues: tuple[Clue, ...]
    proved_verdicts: Mapping[Coord, Status]

    @classmethod
    def from_public_state(cls, state: PublicState) -> PublicKnowledge:
        """Build a `PublicKnowledge` snapshot strictly from public fields of `state`."""
        raise NotImplementedError
