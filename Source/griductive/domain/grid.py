"""Coordinate parsing and grid-size utilities."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Coord:
    """Grid coordinate identified by column letter (`A`..) and 1-based row (`1`..N)."""

    col: str
    row: int


def parse_coord(text: str, size: int | None = None) -> Coord:
    """Parse a coordinate string such as 'A1' and validate bounds if `size` is given."""
    raise NotImplementedError


def format_coord(coord: Coord) -> str:
    """Format a `Coord` back into its canonical string representation (e.g. 'A1')."""
    raise NotImplementedError


def all_coords(size: int) -> tuple[Coord, ...]:
    """Return all coordinates in fixed row-major order for an `N x N` grid."""
    raise NotImplementedError


def coord_to_index(coord: Coord, size: int) -> int:
    """Convert a `Coord` into its 0-based row-major cell index (`0 .. size*size - 1`)."""
    raise NotImplementedError


def index_to_coord(index: int, size: int) -> Coord:
    """Convert a 0-based row-major cell index back into a `Coord`."""
    raise NotImplementedError
