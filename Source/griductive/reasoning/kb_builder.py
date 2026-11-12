"""Knowledge base CNF builder.

Tác dụng:
    Chuyển đổi toàn bộ tri thức trong PublicKnowledge thành một công thức CNF hợp nhất:
    - Encode tất cả các clue đã được lật mở thông qua module Encoder (của Nhật Tân).
    - Bổ sung các unit clauses cho các ô đã có verdict được chấp nhận (+C_i nếu Criminal, -C_i nếu Innocent).

Input:
    - kb: PublicKnowledge
    - varmap: VarMap (tùy chọn; nếu None sẽ khởi tạo mới theo size)
    - direct_threshold: Ngưỡng tổ hợp trực tiếp (mặc định 64)

Output:
    tuple[CNF, VarMap, EncodingStats]: Công thức CNF hoàn chỉnh của KB kèm VarMap và thống kê.
    Được dùng bởi entailment (check_kb_consistent, classify) và logic_agent.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from griductive.domain.types import Status
from griductive.encoding.encoder import Encoder
from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.cnf import CNF


def build_kb_cnf(
    kb: PublicKnowledge,
    varmap: VarMap | None = None,
    direct_threshold: int = 64,
) -> tuple[CNF, VarMap, EncodingStats]:
    """Xây dựng công thức CNF từ PublicKnowledge hiện tại.

    Args:
        kb: Đối tượng tri thức công khai chứa clue đã mở và verdict đã chứng minh.
        varmap: Bản đồ ánh xạ biến (nếu chưa truyền vào, sẽ tạo mới).
        direct_threshold: Ngưỡng số clause để chọn phương pháp cardinality encoding.

    Returns:
        tuple[CNF, VarMap, EncodingStats]: Công thức CNF, VarMap đã cập nhật, và thống kê biến/clause.
    """
    if varmap is None:
        varmap = VarMap(kb.size)

    encoder = Encoder(varmap=varmap, direct_threshold=direct_threshold)
    cnf, stats = encoder.encode(kb.revealed_clues)

    # Bổ sung các unit clause cho các ô đã được lật mở
    for coord, status in kb.proved_verdicts.items():
        var_id = varmap.coord_to_var(coord)
        unit_lit = var_id if status == Status.CRIMINAL else -var_id
        cnf.add_clause([unit_lit])

    # Cập nhật số clause trong stats
    final_stats = EncodingStats(
        primary_vars=stats.primary_vars,
        aux_vars=stats.aux_vars,
        clauses=len(cnf.clauses),
    )
    return cnf, varmap, final_stats
