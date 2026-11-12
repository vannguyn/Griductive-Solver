"""Agent package exports.

Layer 4: Logic Agent, Hint generation, Trace logging, and PublicGame protocol.
"""

from griductive.agent.hint import Hint, suggest_hint
from griductive.agent.logic_agent import AutoSolveStep, LogicAgent
from griductive.agent.ports import PublicGame
from griductive.agent.trace import SolveTrace, TraceSatQuery, TraceStep

__all__ = [
    "PublicGame",
    "Hint",
    "suggest_hint",
    "TraceSatQuery",
    "TraceStep",
    "SolveTrace",
    "AutoSolveStep",
    "LogicAgent",
]
