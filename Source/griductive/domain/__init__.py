"""Domain module exports.

Layer 0: Pure domain types, coordinates, regions, clue interface, and public state.
"""

from griductive.domain.clue import Clue
from griductive.domain.errors import (
    GriductiveError,
    InconsistentKBError,
    InvalidClueError,
    InvalidCoordError,
    InvalidPuzzleError,
    SolverTimeoutError,
)
from griductive.domain.grid import (
    Coord,
    all_coords,
    coord_to_row_major_index,
    format_coord,
    index_to_coord,
    parse_coord,
    validate_coord,
)
from griductive.domain.public_state import PublicCell, PublicState, VerdictOutcome
from griductive.domain.regions import RegionSpec, resolve_region
from griductive.domain.types import (
    Classification,
    RegionKind,
    SolveStatus,
    Status,
    UniquenessResult,
    VerdictResult,
)

__all__ = [
    "Status",
    "RegionKind",
    "Classification",
    "VerdictResult",
    "SolveStatus",
    "UniquenessResult",
    "Coord",
    "parse_coord",
    "format_coord",
    "validate_coord",
    "all_coords",
    "coord_to_row_major_index",
    "index_to_coord",
    "RegionSpec",
    "resolve_region",
    "Clue",
    "PublicCell",
    "PublicState",
    "VerdictOutcome",
    "GriductiveError",
    "InvalidCoordError",
    "InvalidClueError",
    "InvalidPuzzleError",
    "InconsistentKBError",
    "SolverTimeoutError",
]
