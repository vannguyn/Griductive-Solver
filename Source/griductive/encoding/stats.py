"""Encoding statistics data structure.

Tác dụng:
    Lưu trữ số liệu thống kê về quá trình mã hóa CNF:
    số biến chính (primary_vars = N*N), số biến phụ được cấp phát (aux_vars),
    và tổng số mệnh đề CNF (clauses).

Input:
    Các số nguyên từ VarMap và Encoder.

Output:
    Dataclass EncodingStats.
    Bắt buộc cho báo cáo đồ án và thống kê thí nghiệm (Rule 4).

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class EncodingStats:
    """Thống kê chi tiết về kích thước của công thức CNF đã mã hóa.

    Attributes:
        primary_vars: Số biến đại diện cho nhân vật ô cờ (luôn cố định bằng N*N).
        aux_vars: Số biến phụ (auxiliary variables) được sinh thêm cho cardinality/extension.
        clauses: Tổng số mệnh đề CNF sinh ra.
    """
    primary_vars: int = 0
    aux_vars: int = 0
    clauses: int = 0

    @property
    def total_vars(self) -> int:
        """Tổng số biến (biến chính + biến phụ)."""
        return self.primary_vars + self.aux_vars
