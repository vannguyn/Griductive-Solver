"""SAT solver performance statistics data structure.

Tác dụng:
    Định nghĩa cấu trúc lưu vết thống kê hoạt động của thuật toán DPLL:
    số lần ra quyết định (decisions), số bước lan truyền đơn vị (unit propagations),
    số lần quay lui (backtracks), và thời gian thực thi (runtime_ms).

Input:
    Các giá trị đếm nguyên và thời gian thực thi từ DPLLSolver hoặc CountingSolver.

Output:
    Dataclass SolverStats.
    Được trả về bên trong SatResult cho reasoning, agent, experiments để xuất bảng báo cáo.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SolverStats:
    """Thống kê chi tiết của một lượt giải SAT.

    Attributes:
        decisions: Số lần chọn biến và gán nhánh giả định (branching).
        propagations: Số literal được suy diễn gán giá trị tự động qua Unit Propagation.
        backtracks: Số lần quay lui khi gặp xung đột (mệnh đề rỗng).
        runtime_ms: Thời gian chạy tính bằng mili-giây (ms).
    """
    decisions: int = 0
    propagations: int = 0
    backtracks: int = 0
    runtime_ms: float = 0.0
