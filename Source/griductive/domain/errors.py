"""Custom exception hierarchy for Griductive Solver.

Tác dụng:
    Định nghĩa cây ngoại lệ chuẩn để phân loại các lỗi phát sinh trong toàn bộ ứng dụng:
    lỗi tọa độ, lỗi định dạng clue, lỗi cấu trúc puzzle, lỗi mâu thuẫn tri thức, lỗi quá giờ.

Input:
    Các tham số thông báo lỗi khi có exception được ném ra.

Output:
    Các lớp Exception kế thừa GriductiveError.
    Được bắt và xử lý bởi loader, engine, session, GUI và các script kiểm thử.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""


class GriductiveError(Exception):
    """Ngoại lệ gốc cho toàn bộ hệ thống Griductive Solver."""
    pass


class InvalidCoordError(GriductiveError):
    """Ngoại lệ ném ra khi tọa độ ô không đúng định dạng hoặc nằm ngoài biên lưới."""
    pass


class InvalidClueError(GriductiveError):
    """Ngoại lệ ném ra khi manh mối có cú pháp sai, tham số k không hợp lệ hoặc thiếu trường."""
    pass


class InvalidPuzzleError(GriductiveError):
    """Ngoại lệ ném ra khi file JSON của puzzle vi phạm schema hoặc mâu thuẫn giải pháp ẩn."""
    pass


class InconsistentKBError(GriductiveError):
    """Ngoại lệ ném ra khi cơ sở tri thức (KB) tự mâu thuẫn (UNSAT ngay từ đầu wave)."""
    pass


class SolverTimeoutError(GriductiveError):
    """Ngoại lệ ném ra khi DPLL solver chạy quá thời gian (deadline) quy định."""
    pass
