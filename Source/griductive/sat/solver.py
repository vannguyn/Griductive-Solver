"""SatSolver Protocol and CountingSolver decorator.

Tác dụng:
    Định nghĩa Protocol chuẩn cho mọi SAT Solver và lớp CountingSolver giúp bọc một solver bất kỳ
    để tích lũy số lượng gọi (calls), tổng decisions, propagations, backtracks và tổng runtime.

Input:
    Đối tượng CNF, danh sách giả định assumptions, và deadline (thời điểm hết hạn bằng time.perf_counter()).

Output:
    SatResult kèm thống kê tích lũy.
    Được sử dụng bởi reasoning (entailment, uniqueness), logic_agent và experiments.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

import time
from collections.abc import Sequence
from typing import Protocol
from griductive.sat.cnf import CNF, SatResult, SatStatus
from griductive.sat.stats import SolverStats


class SatSolver(Protocol):
    """Protocol chuẩn cho các bộ giải SAT."""

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Giải công thức CNF với các giả định ban đầu và thời hạn deadline.

        Args:
            cnf: Công thức CNF cần giải.
            assumptions: Danh sách các literal giả định bắt buộc phải True (VD: [1, -2]).
            deadline: Thời điểm hết hạn tính bằng time.perf_counter(). Nếu quá hạn, trả TIMEOUT.

        Returns:
            SatResult: Chứa status (SAT/UNSAT/TIMEOUT), model nếu SAT, và stats.
        """
        ...


class CountingSolver:
    """Lớp bọc (wrapper) đo đếm số liệu thống kê tích lũy cho SatSolver."""

    def __init__(self, inner_solver: SatSolver) -> None:
        self.inner_solver = inner_solver
        self.calls: int = 0
        self.total_decisions: int = 0
        self.total_propagations: int = 0
        self.total_backtracks: int = 0
        self.total_runtime_ms: float = 0.0
        self.last_stats: SolverStats | None = None

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Gọi solver bên trong và tích lũy các chỉ số đo đếm."""
        self.calls += 1
        start_t = time.perf_counter()
        res = self.inner_solver.solve(cnf, assumptions, deadline)
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        if res.stats:
            self.total_decisions += res.stats.decisions
            self.total_propagations += res.stats.propagations
            self.total_backtracks += res.stats.backtracks
            self.total_runtime_ms += res.stats.runtime_ms
            self.last_stats = res.stats
        else:
            self.total_runtime_ms += elapsed_ms
            self.last_stats = SolverStats(runtime_ms=elapsed_ms)

        return res

    def reset_counts(self) -> None:
        """Đặt lại toàn bộ các bộ đếm về 0."""
        self.calls = 0
        self.total_decisions = 0
        self.total_propagations = 0
        self.total_backtracks = 0
        self.total_runtime_ms = 0.0
        self.last_stats = None
