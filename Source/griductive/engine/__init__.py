"""Engine package exports.

Layer 5: Hidden puzzle state, integrity loader, and GameEngine.
"""

from griductive.engine.game_engine import GameEngine
from griductive.engine.loader import load_puzzle_file, load_puzzle_from_dict
from griductive.engine.puzzle import Character, Puzzle

__all__ = [
    "Character",
    "Puzzle",
    "load_puzzle_from_dict",
    "load_puzzle_file",
    "GameEngine",
]
