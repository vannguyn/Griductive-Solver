"""Entailment checking and cell classification based on SAT queries.

Tác dụng:
    Thực hiện suy diễn logic theo đúng chuẩn §3.4 của đề bài:
    - Kiểm tra tính nhất quán ban đầu của KB: check_kb_consistent(cnf_kb, solver).
    - Phân loại trạng thái ô thông qua 2 truy vấn giả định (assumptions):
        + Truy vấn 1: Giả sử C_i = False (assumption [-var_id]). Nếu UNSAT -> KB |= C_i (CRIMINAL).
        + Truy vấn 2: Giả sử C_i = True (assumption [+var_id]). Nếu UNSAT -> KB |= NOT C_i (INNOCENT).
        + Cả hai đều SAT -> UNKNOWN.
        + Cả hai đều UNSAT -> INCONSISTENT.
        + Có truy vấn TIMEOUT -> TIMEOUT (tuyệt đối không nhầm thành UNSAT).

Input:
    - cnf_kb: Công thức CNF của cơ sở tri thức hiện tại
    - var_id: ID biến chính của ô cần kiểm tra (1..N*N)
    - solver: Đối tượng thỏa mãn SatSolver Protocol
    - deadline: Thời điểm hết hạn

Output:
    ClassifyOutcome(classification=Classification, queries=tuple[SatQuery, ...]).
    Được logic_agent, hint, game_engine sử dụng.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from dataclasses import dataclass
from griductive.domain.types import Classification
from griductive.sat.cnf import CNF, SatStatus
from griductive.sat.solver import SatSolver


@dataclass(frozen=True)
class SatQuery:
    """Chi tiết một lượt truy vấn SAT có giả định.

    Attributes:
        var_id: ID của biến chính đang được khảo sát.
        assumed_literal: Literal được thêm vào giả định (+var_id hoặc -var_id).
        status: Kết quả trả về từ solver (SAT, UNSAT, hoặc TIMEOUT).
    """
    var_id: int
    assumed_literal: int
    status: SatStatus


@dataclass(frozen=True)
class ClassifyOutcome:
    """Kết quả phân loại logic của một ô kèm theo toàn bộ nhật ký truy vấn SAT.

    Attributes:
        classification: Kết luận phân loại (CRIMINAL, INNOCENT, UNKNOWN, INCONSISTENT, TIMEOUT).
        queries: Tuple các SatQuery đã thực hiện (dùng để ghi log Trace theo PDF §4.4).
    """
    classification: Classification
    queries: tuple[SatQuery, ...]


def check_kb_consistent(
    cnf_kb: CNF,
    solver: SatSolver,
    deadline: float | None = None,
) -> SatStatus:
    """Kiểm tra xem KB hiện tại có tự mâu thuẫn hay không (SAT hay UNSAT).

    Args:
        cnf_kb: Công thức CNF của KB.
        solver: Bộ giải SAT.
        deadline: Thời điểm deadline.

    Returns:
        SatStatus: SAT nếu KB có nghiệm, UNSAT nếu tự mâu thuẫn, hoặc TIMEOUT.
    """
    res = solver.solve(cnf_kb, assumptions=(), deadline=deadline)
    return res.status


def classify(
    cnf_kb: CNF,
    var_id: int,
    solver: SatSolver,
    deadline: float | None = None,
) -> ClassifyOutcome:
    """Phân loại trạng thái của biến var_id dựa trên 2 truy vấn entailment chuẩn.

    Args:
        cnf_kb: Công thức CNF của KB.
        var_id: ID biến đại diện cho nhân vật ô bàn cờ.
        solver: Bộ giải SAT.
        deadline: Thời hạn deadline.

    Returns:
        ClassifyOutcome: Chứa nhãn kết luận và danh sách các query đã chạy.
    """
    queries: list[SatQuery] = []

    # Truy vấn 1: Giả sử C_i là Innocent (assumed_literal = -var_id)
    # Nếu KB AND -var_id là UNSAT -> KB ép C_i phải là CRIMINAL
    res_neg = solver.solve(cnf_kb, assumptions=[-var_id], deadline=deadline)
    queries.append(SatQuery(var_id=var_id, assumed_literal=-var_id, status=res_neg.status))

    if res_neg.status == SatStatus.TIMEOUT:
        return ClassifyOutcome(Classification.TIMEOUT, tuple(queries))

    # Truy vấn 2: Giả sử C_i là Criminal (assumed_literal = +var_id)
    # Nếu KB AND +var_id là UNSAT -> KB ép C_i phải là INNOCENT
    res_pos = solver.solve(cnf_kb, assumptions=[var_id], deadline=deadline)
    queries.append(SatQuery(var_id=var_id, assumed_literal=var_id, status=res_pos.status))

    if res_pos.status == SatStatus.TIMEOUT:
        return ClassifyOutcome(Classification.TIMEOUT, tuple(queries))

    is_neg_unsat = (res_neg.status == SatStatus.UNSAT)
    is_pos_unsat = (res_pos.status == SatStatus.UNSAT)

    if is_neg_unsat and not is_pos_unsat:
        return ClassifyOutcome(Classification.CRIMINAL, tuple(queries))
    elif is_pos_unsat and not is_neg_unsat:
        return ClassifyOutcome(Classification.INNOCENT, tuple(queries))
    elif not is_neg_unsat and not is_pos_unsat:
        return ClassifyOutcome(Classification.UNKNOWN, tuple(queries))
    else:
        # Cả hai giả định đều UNSAT -> Mâu thuẫn
        return ClassifyOutcome(Classification.INCONSISTENT, tuple(queries))
