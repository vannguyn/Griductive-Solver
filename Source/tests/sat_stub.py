"""Bộ giải SAT backtracking tối giản dùng riêng cho test của engine/session.

Tác dụng:
    Cho phép kiểm thử GameEngine/GameSession độc lập với DPLLSolver của Minh.
    Chỉ đúng đắn, không tối ưu; đủ nhanh cho lưới 3x3.
"""

import time
from collections.abc import Sequence
from griductive.sat.cnf import CNF, SatResult, SatStatus


class StubSolver:
    """SatSolver (theo Protocol) cài bằng quay lui đơn giản."""

    def solve(
        self,
        cnf: CNF,
        assumptions: Sequence[int] = (),
        deadline: float | None = None,
    ) -> SatResult:
        """Giải CNF với assumptions; trả SAT kèm model đầy đủ hoặc UNSAT."""
        assign: dict[int, bool] = {}
        for lit in assumptions:
            if assign.get(abs(lit), lit > 0) != (lit > 0):
                return SatResult(SatStatus.UNSAT)
            assign[abs(lit)] = lit > 0

        def conflict(a: dict[int, bool]) -> bool:
            for clause in cnf.clauses:
                if all(abs(l) in a and a[abs(l)] != (l > 0) for l in clause):
                    return True
            return False

        def search(a: dict[int, bool], var: int) -> dict[int, bool] | None:
            if deadline is not None and time.perf_counter() > deadline:
                raise TimeoutError
            if conflict(a):
                return None
            if var > cnf.num_vars:
                return dict(a)
            if var in a:
                return search(a, var + 1)
            for val in (False, True):
                a[var] = val
                res = search(a, var + 1)
                if res is not None:
                    return res
                del a[var]
            return None

        try:
            model = search(assign, 1)
        except TimeoutError:
            return SatResult(SatStatus.TIMEOUT)
        if model is None:
            return SatResult(SatStatus.UNSAT)
        return SatResult(SatStatus.SAT, model)
