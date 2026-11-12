"""Benchmark metrics data structures.

Tác dụng:
    Định nghĩa cấu trúc lưu trữ 6 nhóm chỉ số thực nghiệm bắt buộc theo yêu cầu đề bài:
    1. Nhóm Encoding: primary_vars, aux_vars, clauses
    2. Nhóm SAT: total_sat_calls
    3. Nhóm DPLL: total_decisions, total_propagations, total_backtracks
    4. Nhóm Agent: steps, reveal_waves
    5. Nhóm Runtime: encode_ms, solve_ms, total_runtime_ms
    6. Nhóm Outcome: solve_status (SOLVED, STUCK, INCONSISTENT, TIMEOUT).

Input:
    Số liệu từ Encoder, CountingSolver, và SolveTrace.

Output:
    Dataclass PuzzleMetrics.
    Được runner gom lại và export xuất ra CSV / LaTeX / biểu đồ.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

from dataclasses import dataclass
from griductive.domain.types import SolveStatus


@dataclass(frozen=True)
class PuzzleMetrics:
    """Tập hợp đầy đủ 6 nhóm chỉ số thực nghiệm cho một lượt chạy puzzle."""
    puzzle_id: str
    grid_size: int

    # 1. Encoding
    primary_vars: int
    aux_vars: int
    clauses: int

    # 2. SAT
    total_sat_calls: int

    # 3. DPLL
    total_decisions: int
    total_propagations: int
    total_backtracks: int

    # 4. Agent
    reasoning_steps: int
    reveal_waves: int

    # 5. Runtime
    encode_time_ms: float
    solve_time_ms: float
    total_runtime_ms: float

    # 6. Outcome
    outcome: SolveStatus
