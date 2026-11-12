"""Domain-specific exceptions."""


class GriductiveError(Exception):
    """Base exception for all Griductive Solver domain and validation errors."""


class InvalidCoordError(GriductiveError):
    """Raised when a coordinate string or index is malformed or out of bounds."""


class InvalidClueError(GriductiveError):
    """Raised when a clue definition or its target region is invalid."""


class InvalidPuzzleError(GriductiveError):
    """Raised when puzzle JSON schema, metadata, or solution consistency fails."""
