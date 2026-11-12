"""Re-export Clue base class from domain.

Tác dụng:
    Re-export lớp trừu tượng Clue từ domain.clue sang package clues
    để các module trong clues tiện import mà không phá vỡ tính phân tầng DAG.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from griductive.domain.clue import Clue

__all__ = ["Clue"]
