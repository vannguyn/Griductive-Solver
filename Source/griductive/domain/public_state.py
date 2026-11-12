"""Safe public state boundary exposed to GUI and agent."""

from __future__ import annotations

from dataclasses import dataclass

from griductive.domain.clue import Clue
from griductive.domain.grid import Coord
from griductive.domain.types import SolveStatus, Status, VerdictResult


@dataclass(frozen=True)
class PublicCell:
    """Publicly visible state of a single cell on the game board."""

    coord: Coord
    name: str
    job: str
    revealed: bool
    status: Status | None


@dataclass(frozen=True)
class PublicState:
    """Sanitized game state containing only revealed cards and unlocked clues."""

    puzzle_id: str
    size: int
    cells: tuple[PublicCell, ...]
    revealed_clues: tuple[Clue, ...]
    solve_status: SolveStatus


@dataclass(frozen=True)
class VerdictOutcome:
    """Result of submitting a verdict, including updated public state and unlocked clue."""

    result: VerdictResult
    cell: Coord
    revealed_clue: Clue | None
    public_state: PublicState
    message: str = ""
