"""High-level CNF Encoder.

Tác dụng:
    Lớp điều phối chính quá trình mã hóa tập hợp các Clue thành công thức CNF hoàn chỉnh:
    - Nhận danh sách các Clue.
    - Gọi clue_encoders cho từng clue và thu thập các clause.
    - Đóng gói thành CNF(num_vars=varmap.total_vars, clauses=all_clauses)
      kèm EncodingStats.

Input:
    Danh sách clues: Sequence[Clue] và đối tượng VarMap.

Output:
    tuple[CNF, EncodingStats].
    Được gọi bởi kb_builder và validate_puzzle.

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from collections.abc import Sequence
from griductive.clues.base import Clue
from griductive.encoding.clue_encoders import encode_single_clue
from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import CNF, Clause


class Encoder:
    """Bộ mã hóa tập hợp các Clue sang CNF."""

    def __init__(self, varmap: VarMap, direct_threshold: int = 64) -> None:
        self.varmap = varmap
        self.direct_threshold = direct_threshold

    def encode(self, clues: Sequence[Clue]) -> tuple[CNF, EncodingStats]:
        """Mã hóa toàn bộ danh sách manh mối sang CNF và trả về thống kê.

        Args:
            clues: Danh sách các đối tượng Clue cần mã hóa.

        Returns:
            tuple[CNF, EncodingStats]: Công thức CNF và thống kê số biến chính, biến phụ, mệnh đề.
        """
        all_clauses: list[Clause] = []
        for clue in clues:
            cls = encode_single_clue(clue, self.varmap, self.direct_threshold)
            all_clauses.extend(cls)

        cnf = CNF(num_vars=self.varmap.total_vars, clauses=all_clauses)
        stats = EncodingStats(
            primary_vars=self.varmap.num_primary_vars,
            aux_vars=self.varmap.num_aux_vars,
            clauses=len(all_clauses),
        )
        return cnf, stats
