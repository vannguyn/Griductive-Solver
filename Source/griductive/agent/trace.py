"""Trace logging data structures for Auto-Solve reasoning steps.

Tác dụng:
    Định nghĩa các cấu trúc dữ liệu lưu vết chi tiết từng bước suy diễn tự động:
    TraceSatQuery, TraceStep (chứa chi tiết các truy vấn SAT, clue liên quan, verdict, runtime),
    và SolveTrace (chứa toàn bộ chuỗi các bước cùng tổng số liệu SAT calls, decisions, waves).
    Đáp ứng chuẩn yêu cầu ghi nhật ký của PDF §4.4.

Input:
    Thông tin từng wave suy luận từ logic_agent.

Output:
    SolveTrace và TraceStep.
    Được xuất ra file JSON log tại Source/results/traces/ và hiển thị trên GUI.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

from dataclasses import dataclass, field
from griductive.domain.grid import Coord
from griductive.domain.types import Classification, SolveStatus, Status, VerdictResult
from griductive.sat.cnf import SatStatus


@dataclass(frozen=True)
class TraceSatQuery:
    """Ghi nhận một lượt truy vấn SAT cụ thể trong quá trình phân loại một ô.

    Attributes:
        coord: Tọa độ ô đang được kiểm tra giả định.
        assumed_status: Giả định được đưa vào (CRIMINAL hoặc INNOCENT).
        status: Kết quả trả về từ DPLL solver (SAT, UNSAT, hoặc TIMEOUT).
    """
    coord: Coord
    assumed_status: Status
    status: SatStatus


@dataclass(frozen=True)
class TraceStep:
    """Nhật ký chi tiết của một bước suy luận và lật mở ô thành công.

    Attributes:
        step: Thứ tự bước (1, 2, 3...).
        wave: Lượt suy diễn (Wave t).
        cell: Ô được chọn để nộp kết luận.
        classification: Kết luận suy diễn được (CRIMINAL hoặc INNOCENT).
        active_clue_ids: Danh sách ID các clue đang có hiệu lực trong KB tại thời điểm đó.
        sat_queries: Danh sách các truy vấn SAT đã thực hiện cho ô này.
        verdict_result: Kết quả phản hồi từ game (thường là ACCEPTED).
        revealed_clue_id: ID của clue mới vừa được mở ra (nếu có).
        runtime_ms: Thời gian thực hiện bước này tính bằng ms.
    """
    step: int
    wave: int
    cell: Coord
    classification: Classification
    active_clue_ids: tuple[str, ...]
    sat_queries: tuple[TraceSatQuery, ...]
    verdict_result: VerdictResult
    revealed_clue_id: str | None
    runtime_ms: float


@dataclass
class SolveTrace:
    """Toàn bộ nhật ký hành trình giải một puzzle từ đầu đến cuối.

    Attributes:
        puzzle_id: Định danh puzzle.
        solve_status: Trạng thái kết thúc (SOLVED, STUCK, INCONSISTENT, TIMEOUT).
        steps: Danh sách các bước TraceStep đã thực hiện.
        total_sat_calls: Tổng số lần gọi SAT solver trong suốt quá trình.
        total_decisions: Tổng số lần ra quyết định branching của DPLL.
        total_propagations: Tổng số bước lan truyền đơn vị (Unit Propagation).
        total_backtracks: Tổng số lần quay lui.
        reveal_waves: Tổng số wave suy luận.
        total_runtime_ms: Tổng thời gian giải tự động (ms).
    """
    puzzle_id: str
    solve_status: SolveStatus = SolveStatus.RUNNING
    steps: list[TraceStep] = field(default_factory=list)
    total_sat_calls: int = 0
    total_decisions: int = 0
    total_propagations: int = 0
    total_backtracks: int = 0
    reveal_waves: int = 0
    total_runtime_ms: float = 0.0
