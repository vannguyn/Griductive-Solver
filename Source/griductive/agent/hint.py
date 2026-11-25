"""Hint generation system based purely on Public Knowledge entailment.

Tác dụng:
    Gợi ý bước đi an toàn cho người chơi khi bấm nút Hint trên GUI:
    - Tìm kiếm ô chưa lật đầu tiên (theo thứ tự row-major) mà trạng thái đã bị ÉP BUỘC
      bởi tri thức công khai hiện tại (entailed by PublicKnowledge).
    - Bảo đảm Rule 5: Tuyệt đối không đọc solution ẩn, không đoán mò.
    - Trả về đối tượng Hint hoặc None nếu chưa có ô nào suy ra được.

Input:
    PublicKnowledge, SatSolver, và deadline.

Output:
    Hint(cell, suggested_status, related_clue_ids, reason) hoặc None.
    Được gọi bởi GameSession.hint().

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

from dataclasses import dataclass
from griductive.domain.grid import Coord, all_coords
from griductive.domain.types import Classification, Status
from griductive.reasoning.entailment import check_kb_consistent, classify
from griductive.reasoning.kb_builder import build_kb_cnf
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.cnf import SatStatus
from griductive.sat.solver import SatSolver


@dataclass(frozen=True)
class Hint:
    """Thông tin gợi ý một bước đi hợp lệ.

    Attributes:
        cell: Tọa độ ô nên lật ("A1".."E5").
        suggested_status: Trạng thái chắc chắn đúng (CRIMINAL hoặc INNOCENT).
        related_clue_ids: Danh sách ID các clue làm căn cứ suy diễn.
        reason: Diễn giải lý do logic (mặc định: "ENTAILED_BY_PUBLIC_KB").
    """
    cell: Coord
    suggested_status: Status
    related_clue_ids: tuple[str, ...]
    reason: str = "ENTAILED_BY_PUBLIC_KB"


def suggest_hint(
    pk: PublicKnowledge,
    solver: SatSolver,
    deadline: float | None = None,
) -> Hint | None:
    """Tìm ô bị ép buộc logic đầu tiên theo thứ tự row-major để đưa ra gợi ý."""
    cnf_kb, varmap, _ = build_kb_cnf(pk)

    # Kiểm tra tính thỏa mãn của KB hiện tại
    if check_kb_consistent(cnf_kb, solver, deadline) != SatStatus.SAT:
        return None

    coords = all_coords(pk.size)
    for c in coords:
        if c in pk.proved_verdicts:
            continue  # Ô này đã được mở rồi

        var_id = varmap.coord_to_var(c)
        outcome = classify(cnf_kb, var_id, solver, deadline)

        if outcome.classification in (Classification.CRIMINAL, Classification.INNOCENT):
            suggested = Status(outcome.classification.value)
            active_ids = tuple(clue.id for clue in pk.revealed_clues)
            return Hint(
                cell=c,
                suggested_status=suggested,
                related_clue_ids=active_ids,
                reason="ENTAILED_BY_PUBLIC_KB",
            )

    return None
