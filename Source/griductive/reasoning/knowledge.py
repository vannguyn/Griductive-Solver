"""Public knowledge structure for logical deduction.

Tác dụng:
    Đại diện cho cơ sở tri thức công khai (Public Knowledge) tại một thời điểm của ván chơi.
    Chỉ chứa các manh mối đã được lật mở (revealed_clues) và các phán quyết đã được
    chứng minh hợp lệ (proved_verdicts).
    Tuyệt đối không chứa đáp án ẩn hay manh mối còn úp.

Input:
    PublicState từ GameEngine hoặc GameSession.

Output:
    Đối tượng PublicKnowledge.
    Được chuyển vào kb_builder để chuyển đổi sang CNF, và cho suggest_hint.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from dataclasses import dataclass
from griductive.domain.clue import Clue
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState
from griductive.domain.types import Status


@dataclass(frozen=True)
class PublicKnowledge:
    """Tập hợp tri thức công khai tại một bước chơi.

    Attributes:
        puzzle_id: Mã định danh puzzle.
        size: Kích thước lưới N.
        revealed_clues: Các clue đã được mở.
        proved_verdicts: Ánh xạ tọa độ -> Status của các ô đã được lật mở thành công.
    """
    puzzle_id: str
    size: int
    revealed_clues: tuple[Clue, ...]
    proved_verdicts: dict[Coord, Status]

    @classmethod
    def from_public_state(cls, state: PublicState) -> "PublicKnowledge":
        """Trích xuất PublicKnowledge an toàn từ một PublicState."""
        proved: dict[Coord, Status] = {}
        for cell in state.cells:
            if cell.revealed and cell.status is not None:
                proved[cell.coord] = cell.status
        return cls(
            puzzle_id=state.puzzle_id,
            size=state.size,
            revealed_clues=state.revealed_clues,
            proved_verdicts=proved,
        )
