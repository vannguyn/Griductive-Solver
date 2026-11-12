"""Public game state and verdict communication structures.

Tác dụng:
    Định nghĩa các cấu trúc dữ liệu công khai (Tầng 0) thể hiện trạng thái bàn chơi mà
    Agent và GUI được phép quan sát.
    Bảo đảm Rule 1: Tuyệt đối không chứa đáp án ẩn (solution) hay manh mối chưa lật.

Input:
    Thông tin từ GameEngine khi khởi tạo hoặc khi một ô được lật mở thành công.

Output:
    PublicCell, PublicState, VerdictOutcome.
    Được trả về cho GameSession, LogicAgent, Hint và PyQt6 GUI.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

from dataclasses import dataclass
from griductive.domain.clue import Clue
from griductive.domain.grid import Coord
from griductive.domain.types import SolveStatus, Status, VerdictResult


@dataclass(frozen=True)
class PublicCell:
    """Trạng thái công khai của một ô trên lưới bàn cờ.

    Attributes:
        coord: Tọa độ ô ("A1".."E5").
        name: Tên nhân vật (ví dụ: "Abel", "Priya").
        job: Nghề nghiệp nhân vật (ví dụ: "Detective", "Banker").
        revealed: Đã được lật mở hay chưa (True = đã lật, False = đang úp).
        status: CRIMINAL hoặc INNOCENT nếu đã lật (revealed=True), hoặc None nếu đang úp.
    """
    coord: Coord
    name: str
    job: str
    revealed: bool
    status: Status | None = None


@dataclass(frozen=True)
class PublicState:
    """Toàn bộ trạng thái công khai của bàn chơi tại một thời điểm (Wave t).

    Attributes:
        puzzle_id: Định danh của puzzle (ví dụ: "p01").
        size: Kích thước lưới N (3, 4, hoặc 5).
        cells: Tuple chứa đúng N*N PublicCell theo thứ tự row-major.
        revealed_clues: Tuple chứa các Clue đã được lật mở tính đến thời điểm hiện tại.
        solve_status: Trạng thái của game (RUNNING, SOLVED, STUCK, INCONSISTENT, TIMEOUT).
    """
    puzzle_id: str
    size: int
    cells: tuple[PublicCell, ...]
    revealed_clues: tuple[Clue, ...]
    solve_status: SolveStatus = SolveStatus.RUNNING

    def cell_at(self, coord: Coord) -> PublicCell | None:
        """Tìm PublicCell tương ứng với tọa độ cho trước."""
        for c in self.cells:
            if c.coord == coord:
                return c
        return None

    def is_all_revealed(self) -> bool:
        """Kiểm tra xem toàn bộ các ô trong lưới đã được lật mở hay chưa."""
        return all(c.revealed for c in self.cells)


@dataclass(frozen=True)
class VerdictOutcome:
    """Kết quả trả về sau khi người chơi hoặc Agent nộp kết luận về một ô qua submit_verdict.

    Attributes:
        result: Kết quả (ACCEPTED, NOT_PROVABLE, CONTRADICTED, ALREADY_REVEALED).
        cell: Tọa độ ô được nộp verdict.
        revealed_clue: Đối tượng Clue vừa được lật mở nếu result == ACCEPTED; ngược lại None.
        public_state: Trạng thái công khai mới nhất của bàn chơi sau thao tác.
        message: Thông điệp mô tả giải thích kết quả (hữu ích cho GUI/Log).
    """
    result: VerdictResult
    cell: Coord
    revealed_clue: Clue | None
    public_state: PublicState
    message: str = ""
