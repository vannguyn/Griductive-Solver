"""Primary and auxiliary variable allocation."""

from __future__ import annotations

from griductive.domain.grid import Coord


class VarMap:
    """Bijective row-major map for primary cell variables plus auxiliary allocator."""

    size: int

    def __init__(self, size: int) -> None:
        """Initialize variable map for an `N x N` grid (`1..N*N` primary vars)."""
        raise NotImplementedError

    def coord_to_var(self, coord: Coord) -> int:
        """Return positive 1-based SAT variable ID for `coord` in row-major order."""
        raise NotImplementedError

    def var_to_coord(self, var_id: int) -> Coord:
        """Convert a primary SAT variable ID back into its grid `Coord`."""
        raise NotImplementedError

    def new_aux(self) -> int:
        """Allocate and return a fresh auxiliary SAT variable ID above primary vars."""
        raise NotImplementedError

    def primary_var_count(self) -> int:
        """Return total number of primary grid variables (`size * size`)."""
        raise NotImplementedError

    def aux_var_count(self) -> int:
        """Return number of auxiliary variables allocated so far."""
        raise NotImplementedError
