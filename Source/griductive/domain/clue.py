"""Pure domain base contract for puzzle clues."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping

from griductive.domain.grid import Coord


class Clue(ABC):
    """Abstract base interface shared by core and extension clues."""

    id: str
    owner: Coord
    clue_type: str

    @abstractmethod
    def cells(self) -> tuple[Coord, ...]:
        """Return the tuple of grid coordinates referenced by this clue."""

    @abstractmethod
    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        """Evaluate whether this clue holds under a truth assignment (`True` = CRIMINAL)."""
