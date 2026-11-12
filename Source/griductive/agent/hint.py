"""Hint selection without reading the hidden solution."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.grid import Coord
from griductive.domain.types import Status
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.solver import SatSolver


@dataclass(frozen=True)
class Hint:
    """Safe deduction hint derived solely from `PublicKnowledge`."""

    cell: Coord
    suggested_status: Status
    related_clue_ids: tuple[str, ...]
    reason: str


def suggest_hint(
    pk: PublicKnowledge,
    solver: SatSolver,
    deadline: float | None = None,
) -> Hint | None:
    """Return the row-major first entailed cell hint, or `None` if stuck/timed out."""
    raise NotImplementedError
