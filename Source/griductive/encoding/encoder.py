from collections.abc import Sequence
from griductive.clues.base import Clue
from griductive.encoding.clue_encoders import encode_single_clue
from griductive.encoding.stats import EncodingStats
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import CNF, Clause


class Encoder:

    """Mã hóa manh mối bằng một bản đồ biến SAT dùng chung."""
    def __init__(self, varmap: VarMap, direct_threshold: int = 64) -> None:
        self.varmap = varmap
        self.direct_threshold = direct_threshold

    def encode(self, clues: Sequence[Clue]) -> tuple[CNF, EncodingStats]:
        """Trả về CNF cùng số biến và số mệnh đề."""
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
