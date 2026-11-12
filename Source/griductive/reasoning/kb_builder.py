"""Build a CNF knowledge base from public knowledge."""

from __future__ import annotations

from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.cnf import CNF


def build_kb_cnf(
    kb: PublicKnowledge,
    varmap: VarMap | None = None,
    direct_threshold: int = 64,
) -> tuple[CNF, VarMap, EncodingStats]:
    """Encode revealed clues and proved verdicts into an integer CNF KB."""
    raise NotImplementedError
