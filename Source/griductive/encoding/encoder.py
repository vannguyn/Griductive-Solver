"""Top-level clue collection encoder."""

from __future__ import annotations

from collections.abc import Sequence

from griductive.domain.clue import Clue
from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import CNF


class Encoder:
    """Encodes a sequence of `Clue` instances into an integer CNF formula."""

    varmap: VarMap
    direct_threshold: int

    def __init__(self, varmap: VarMap, direct_threshold: int = 64) -> None:
        """Configure encoder with a `VarMap` and clause threshold for direct vs sequential."""
        raise NotImplementedError

    def encode(self, clues: Sequence[Clue]) -> tuple[CNF, EncodingStats]:
        """Encode `clues` into integer `CNF` and `EncodingStats`."""
        raise NotImplementedError
