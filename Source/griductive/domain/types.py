"""Domain enums and core value types.

Tác dụng:
    Định nghĩa các Enum và kiểu dữ liệu cơ sở cho toàn bộ hệ thống Griductive Solver (Tầng 0).
    Mọi module ở các tầng cao hơn đều phụ thuộc vào file này, file này không phụ thuộc module nào khác.

Input:
    Không nhận input từ module khác.

Output:
    Cung cấp các Enum: Status, RegionKind, Classification, VerdictResult, SolveStatus, UniquenessResult.
    Được sử dụng bởi tất cả các module trong domain, clues, reasoning, agent, engine, app, gui.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

from enum import Enum


class Status(str, Enum):
    """Trạng thái nhân vật trên một ô lưới."""
    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"


class RegionKind(str, Enum):
    """Loại vùng tham chiếu của manh mối."""
    ROW = "row"
    COLUMN = "column"
    NEIGHBORS = "neighbors"
    EXPLICIT = "explicit"


class Classification(str, Enum):
    """Kết quả phân loại một ô qua suy diễn entailment theo đề §3.4.

    - CRIMINAL: KB |= C_i (KB AND NOT C_i is UNSAT)
    - INNOCENT: KB |= NOT C_i (KB AND C_i is UNSAT)
    - UNKNOWN: Cả hai giả định đều SAT (chưa đủ dữ kiện để khẳng định)
    - INCONSISTENT: KB tự mâu thuẫn hoặc cả hai giả định đều UNSAT
    - TIMEOUT: DPLL solver vượt quá deadline cho phép
    """
    CRIMINAL = "CRIMINAL"
    INNOCENT = "INNOCENT"
    UNKNOWN = "UNKNOWN"
    INCONSISTENT = "INCONSISTENT"
    TIMEOUT = "TIMEOUT"


class VerdictResult(str, Enum):
    """Kết quả trả về khi người chơi hoặc Agent nộp kết luận về một ô.

    - ACCEPTED: Verdict đúng và được chứng minh bởi KB hiện tại -> ô được lật.
    - NOT_PROVABLE: Chưa đủ cơ sở logic suy luận từ clue đã lộ (không được đoán).
    - CONTRADICTED: Trái ngược với kết luận bắt buộc bị ép bởi KB hiện tại.
    - ALREADY_REVEALED: Ô này đã được lật mở trước đó.
    """
    ACCEPTED = "ACCEPTED"
    NOT_PROVABLE = "NOT_PROVABLE"
    CONTRADICTED = "CONTRADICTED"
    ALREADY_REVEALED = "ALREADY_REVEALED"


class SolveStatus(str, Enum):
    """Trạng thái tổng thể của quá trình giải tự động (Auto Solve) hoặc Thí nghiệm."""
    RUNNING = "RUNNING"
    SOLVED = "SOLVED"
    STUCK = "STUCK"
    INCONSISTENT = "INCONSISTENT"
    TIMEOUT = "TIMEOUT"


class UniquenessResult(str, Enum):
    """Kết quả kiểm tra tính duy nhất của nghiệm puzzle (Uniqueness Check)."""
    UNIQUE = "UNIQUE"
    MULTIPLE = "MULTIPLE"
    UNSAT = "UNSAT"
    TIMEOUT = "TIMEOUT"
