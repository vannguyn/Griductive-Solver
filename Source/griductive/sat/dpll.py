"""DPLL (Davis-Putnam-Logemann-Loveland) SAT solver implementation.

Tác dụng:
    Bộ giải SAT cốt lõi thực thi thuật toán DPLL thuần túy số nguyên.
    Hỗ trợ Unit Propagation, quay lui (backtracking), xử lý assumptions và kiểm tra deadline.
    Khi kết luận SAT, bảo đảm trả về complete assignment cho các biến 1..num_vars.

Input:
    - cnf: Đối tượng CNF(num_vars, clauses)
    - assumptions: Danh sách các literal giả định (ví dụ: [C_i] hoặc [-C_i])
    - deadline: Thời điểm hết hạn (tính bằng time.perf_counter())

Output:
    SatResult(status=SatStatus, model=dict, stats=SolverStats).
    Được gọi bởi CountingSolver, reasoning (entailment, uniqueness).

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

import time
from collections.abc import Sequence

from griductive.sat.cnf import CNF, SatResult, SatStatus
from griductive.sat.stats import SolverStats


class _DeadlineExceeded(Exception):
    """Dừng tìm kiếm và giữ lại các thống kê đã thu thập."""


class DPLLSolver:
    """Bộ giải DPLL thuần số nguyên."""

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Giải công thức CNF bằng thuật toán DPLL.

        Args:
            cnf: Công thức CNF cần giải.
            assumptions: Danh sách các literal giả định bắt buộc True.
            deadline: Thời điểm deadline (từ time.perf_counter()).

        Returns:
            SatResult: Kết quả phân tích tính thỏa của công thức.
        """
        start_time = time.perf_counter()
        assignment: dict[int, bool] = {}
        decisions = propagations = backtracks = 0

        def check_deadline() -> None:
            if deadline is not None and time.perf_counter() >= deadline:
                raise _DeadlineExceeded

        def propagate() -> tuple[bool, int | None]:
            """Trả về tính nhất quán và biến cần chia nhánh sau khi lan truyền."""
            nonlocal propagations

            while True:
                check_deadline()
                changed = False
                branch_variable = None

                for clause in cnf.clauses:
                    unassigned_literal = None
                    has_other_unassigned_literal = False
                    for literal in clause:
                        check_deadline()
                        value = assignment.get(abs(literal))
                        if value is None:
                            if unassigned_literal is None:
                                unassigned_literal = literal
                            elif literal != unassigned_literal:
                                has_other_unassigned_literal = True
                        elif value == (literal > 0):
                            break
                    else:
                        # Không có literal nào đúng trong mệnh đề này.
                        if unassigned_literal is None:
                            return False, None

                        variable = abs(unassigned_literal)
                        if not has_other_unassigned_literal:
                            assignment[variable] = unassigned_literal > 0
                            propagations += 1
                            changed = True
                        elif branch_variable is None:
                            branch_variable = variable

                if not changed:
                    return True, branch_variable

        def search() -> dict[int, bool] | None:
            """Tìm model hoàn chỉnh hoặc kết luận UNSAT."""
            nonlocal decisions, backtracks

            for literal in assumptions:
                check_deadline()
                variable = abs(literal)
                value = literal > 0
                if assignment.get(variable, value) != value:
                    return None
                assignment[variable] = value

            # Mỗi mục lưu một nhánh False chưa thử và kích thước phép gán trước khi rẽ nhánh.
            alternatives: list[tuple[int, int]] = []
            while True:
                consistent, branch_variable = propagate()
                if consistent:
                    if branch_variable is None:
                        model: dict[int, bool] = {}
                        for variable in range(1, cnf.num_vars + 1):
                            check_deadline()
                            model[variable] = assignment.get(variable, False)
                        return model

                    alternatives.append((branch_variable, len(assignment)))
                    assignment[branch_variable] = True
                elif alternatives:
                    branch_variable, checkpoint = alternatives.pop()
                    # dict.popitem() hoàn tác các phép gán theo thứ tự ngược.
                    while len(assignment) > checkpoint:
                        check_deadline()
                        assignment.popitem()
                    assignment[branch_variable] = False
                    backtracks += 1
                else:
                    return None

                decisions += 1

        try:
            check_deadline()
            model = search()
            check_deadline()
            status = SatStatus.UNSAT if model is None else SatStatus.SAT
        except _DeadlineExceeded:
            model = None
            status = SatStatus.TIMEOUT

        stats = SolverStats(
            decisions=decisions,
            propagations=propagations,
            backtracks=backtracks,
            runtime_ms=(time.perf_counter() - start_time) * 1000.0,
        )
        return SatResult(status=status, model=model, stats=stats)
