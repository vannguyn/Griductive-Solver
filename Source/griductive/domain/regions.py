"""Helpers for rows, columns, neighbors, and explicit regions."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.grid import Coord
from griductive.domain.types import RegionKind


@dataclass(frozen=True)
class RegionSpec:
    """Declarative specification for resolving a target region of grid coordinates."""

    kind: RegionKind
    index: int | None = None
    center: Coord | None = None
    cells: tuple[Coord, ...] = ()


def resolve_region(spec: RegionSpec, size: int) -> tuple[Coord, ...]:
    """Resolve a `RegionSpec` into concrete ordered `Coord` targets on an `N x N` grid."""
    raise NotImplementedError
