"""Domain enums and result types."""

from enum import Enum


class Status(str, Enum):
    """Truth assignment status of a character cell."""

    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"


class Classification(str, Enum):
    """Logical entailment outcome for an unrevealed cell."""

    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"
    UNKNOWN = "UNKNOWN"
    INCONSISTENT = "INCONSISTENT"
    TIMEOUT = "TIMEOUT"


class VerdictResult(str, Enum):
    """Outcome of submitting a player or agent verdict for a cell."""

    ACCEPTED = "ACCEPTED"
    NOT_PROVABLE = "NOT_PROVABLE"
    CONTRADICTED = "CONTRADICTED"
    ALREADY_REVEALED = "ALREADY_REVEALED"


class SolveStatus(str, Enum):
    """Overall game or auto-solve execution status."""

    RUNNING = "RUNNING"
    SOLVED = "SOLVED"
    STUCK = "STUCK"
    INCONSISTENT = "INCONSISTENT"
    TIMEOUT = "TIMEOUT"


class UniquenessResult(str, Enum):
    """Outcome of checking puzzle solution uniqueness."""

    UNIQUE = "UNIQUE"
    MULTIPLE = "MULTIPLE"
    UNSAT = "UNSAT"
    TIMEOUT = "TIMEOUT"


class RegionKind(str, Enum):
    """Supported region specification kinds for clues."""

    ROW = "ROW"
    COLUMN = "COLUMN"
    NEIGHBORS = "NEIGHBORS"
    EXPLICIT = "EXPLICIT"
