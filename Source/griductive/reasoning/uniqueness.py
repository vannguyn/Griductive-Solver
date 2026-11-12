"""Uniqueness verification for puzzle solutions.

Tác dụng:
    Kiểm tra xem một puzzle có đúng DUY NHẤT một nghiệm gán biến chính hay không:
    - Tìm nghiệm đầu tiên M_1 trên công thức CNF đầy đủ.
    - Tạo blocking clause CHỈ trên các biến chính (1..num_primary_vars), không chặn biến phụ:
        blocking_clause = [ -v if M_1[v] else +v for v in 1..num_primary_vars ]
    - Giải lại: nếu UNSAT -> UNIQUE; nếu SAT -> MULTIPLE (nhiều nghiệm); nếu TIMEOUT -> TIMEOUT.

Input:
    - cnf: Công thức CNF đầy đủ của toàn bộ puzzle
    - num_primary_vars: Số biến chính (đúng bằng N*N)
    - solver: Bộ giải SatSolver
    - deadline: Thời hạn deadline

Output:
    UniquenessOutput(result=UniquenessResult, first_model=dict, stats=SolverStats).
    Được gọi bởi experiments/validate_puzzle.py và runner.py.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from dataclasses import dataclass
from griductive.domain.types import UniquenessResult
from griductive.sat.cnf import CNF, SatStatus
from griductive.sat.solver import SatSolver
from griductive.sat.stats import SolverStats


@dataclass(frozen=True)
class UniquenessOutput:
    """Kết quả kiểm tra tính duy nhất của nghiệm.

    Attributes:
        result: UNIQUE, MULTIPLE, UNSAT, hoặc TIMEOUT.
        first_model: Nghiệm đầu tiên tìm được (nếu có).
        stats: Thống kê hiệu năng solver.
    """
    result: UniquenessResult
    first_model: dict[int, bool] | None = None
    stats: SolverStats | None = None


def check_uniqueness(
    cnf: CNF,
    num_primary_vars: int,
    solver: SatSolver,
    deadline: float | None = None,
) -> UniquenessOutput:
    """Kiểm tra nghiệm duy nhất trên các biến chính 1..num_primary_vars.

    Args:
        cnf: Công thức CNF toàn cục của puzzle.
        num_primary_vars: Số lượng biến đại diện nhân vật (N*N).
        solver: Bộ giải SAT.
        deadline: Thời điểm deadline.

    Returns:
        UniquenessOutput: Đánh giá tính duy nhất của nghiệm.
    """
    # 1. Tìm nghiệm đầu tiên
    res1 = solver.solve(cnf, assumptions=(), deadline=deadline)
    if res1.status == SatStatus.UNSAT:
        return UniquenessOutput(result=UniquenessResult.UNSAT, first_model=None, stats=res1.stats)
    if res1.status == SatStatus.TIMEOUT or res1.model is None:
        return UniquenessOutput(result=UniquenessResult.TIMEOUT, first_model=None, stats=res1.stats)

    first_model = res1.model

    # 2. Tạo blocking clause chỉ chặn tổ hợp biến chính
    blocking_clause: list[int] = []
    for var_id in range(1, num_primary_vars + 1):
        is_true = first_model.get(var_id, False)
        # Nếu var_id là True trong nghiệm 1 -> mệnh đề phủ định là -var_id
        # Nếu var_id là False trong nghiệm 1 -> mệnh đề phủ định là +var_id
        blocking_clause.append(-var_id if is_true else var_id)

    # 3. Thêm blocking clause vào bản sao CNF và giải lại
    cnf_blocked = cnf.copy()
    cnf_blocked.add_clause(blocking_clause)

    res2 = solver.solve(cnf_blocked, assumptions=(), deadline=deadline)
    if res2.status == SatStatus.UNSAT:
        return UniquenessOutput(result=UniquenessResult.UNIQUE, first_model=first_model, stats=res2.stats)
    elif res2.status == SatStatus.SAT:
        return UniquenessOutput(result=UniquenessResult.MULTIPLE, first_model=first_model, stats=res2.stats)
    else:
        return UniquenessOutput(result=UniquenessResult.TIMEOUT, first_model=first_model, stats=res2.stats)
