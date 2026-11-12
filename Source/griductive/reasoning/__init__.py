"""Reasoning module exports.

Layer 3: Knowledge representation, KB builder, entailment reasoning, and uniqueness check.
"""

from griductive.reasoning.entailment import (
    ClassifyOutcome,
    SatQuery,
    check_kb_consistent,
    classify,
)
from griductive.reasoning.kb_builder import build_kb_cnf
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.reasoning.uniqueness import UniquenessOutput, check_uniqueness

__all__ = [
    "PublicKnowledge",
    "build_kb_cnf",
    "SatQuery",
    "ClassifyOutcome",
    "check_kb_consistent",
    "classify",
    "UniquenessOutput",
    "check_uniqueness",
]
