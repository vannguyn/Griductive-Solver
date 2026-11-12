"""CNF formula representation and SAT result types.

Tác dụng:
    Định nghĩa công thức dạng hội chuẩn CNF (Conjunctive Normal Form) thuần số nguyên,
    trạng thái kết quả SAT (SatStatus: SAT, UNSAT, TIMEOUT) và cấu trúc SatResult.
    Tuyệt đối không phụ thuộc vào domain hay nghiệp vụ Griductive.

Input:
    Số biến (num_vars) và danh sách các mệnh đề số nguyên clauses: list[list[int]].

Output:
    Các cấu trúc CNF, SatStatus, SatResult.
    Được dùng bởi DPLLSolver, Encoder, Reasoning, Agent.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TypeAlias
from griductive.sat.stats import SolverStats

Literal: TypeAlias = int  # Số nguyên != 0 (dương: biến, âm: phủ định)
Clause: TypeAlias = list[Literal]  # Tuyển của các literal (OR)


class SatStatus(str, Enum):
    """Trạng thái kết quả của một truy vấn giải SAT."""
    SAT = "SAT"
    UNSAT = "UNSAT"
    TIMEOUT = "TIMEOUT"


@dataclass
class CNF:
    """Công thức CNF thuần số nguyên.

    Attributes:
        num_vars: Tổng số biến được khai báo (từ 1 đến num_vars).
        clauses: Danh sách các mệnh đề, mỗi mệnh đề là một list[int].
    """
    num_vars: int
    clauses: list[Clause] = field(default_factory=list)

    def add_clause(self, clause: Clause) -> None:
        """Thêm một mệnh đề vào công thức CNF."""
        self.clauses.append(clause)

    def copy(self) -> "CNF":
        """Tạo bản sao sâu (deep copy) của công thức CNF."""
        return CNF(num_vars=self.num_vars, clauses=[list(c) for c in self.clauses])


@dataclass(frozen=True)
class SatResult:
    """Kết quả trả về sau khi giải một bài toán SAT.

    Attributes:
        status: SAT, UNSAT, hoặc TIMEOUT.
        model: Gán giá trị biến dict[var_id -> bool] (hoàn chỉnh cho 1..num_vars nếu SAT); None nếu UNSAT hoặc TIMEOUT.
        stats: Thống kê solver (decisions, propagations, backtracks, runtime_ms).
    """
    status: SatStatus
    model: dict[int, bool] | None = None
    stats: SolverStats | None = None
