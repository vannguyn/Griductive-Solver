"""Encoding statistics: primary variables, auxiliary variables, and clauses."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodingStats:
    """Summary counts produced by CNF encoding."""

    primary_vars: int
    aux_vars: int
    clauses: int
