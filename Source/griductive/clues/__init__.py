"""Clues package exports.

Layer 1: Clue implementations, semantic evaluators, validation, and parser.
"""

from griductive.clues.base import Clue
from griductive.clues.core import (
    AtLeastClue,
    AtMostClue,
    DifferentClue,
    ExactlyClue,
    FactClue,
    SameClue,
)
from griductive.clues.extensions import (
    CompareCountClue,
    CompoundClue,
    ParityClue,
)
from griductive.clues.parser import parse_clue, parse_clues
from griductive.clues.validator import validate_clue_dict, validate_clue_object

__all__ = [
    "Clue",
    "FactClue",
    "SameClue",
    "DifferentClue",
    "ExactlyClue",
    "AtLeastClue",
    "AtMostClue",
    "ParityClue",
    "CompoundClue",
    "CompareCountClue",
    "validate_clue_dict",
    "validate_clue_object",
    "parse_clue",
    "parse_clues",
]
