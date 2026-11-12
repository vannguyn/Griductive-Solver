"""Encoding package exports.

Layer 2: Mapping variables and translating clues into Conjunctive Normal Form (CNF).
"""

from griductive.encoding.cardinality import encode_cardinality
from griductive.encoding.clue_encoders import encode_single_clue
from griductive.encoding.encoder import Encoder
from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap

__all__ = [
    "VarMap",
    "EncodingStats",
    "Encoder",
    "encode_cardinality",
    "encode_single_clue",
]
