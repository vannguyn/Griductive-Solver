"""Unit tests for pure DPLL SAT Solver.

Tác dụng:
    Kiểm thử thuật toán DPLL thuần số nguyên:
    - So sánh kết quả SAT / UNSAT với thuật toán vét cạn trên các CNF ngẫu nhiên quy mô nhỏ (<= 16 biến).
    - Kiểm thử cơ chế assumptions và deadline timeout.

Input:
    Các đối tượng CNF tổng hợp và giả định assumptions.

Output:
    Khẳng định tính đúng đắn (assert) của DPLLSolver.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

import time
from itertools import count, product
from random import Random
from types import SimpleNamespace

import pytest

from griductive.sat import dpll
from griductive.sat.cnf import CNF, SatStatus
from griductive.sat.dpll import DPLLSolver


def test_dpll_trivial_sat() -> None:
    """Kiểm tra CNF đơn giản hiển nhiên SAT: (1 or 2) and (-1 or 2)."""
    solver = DPLLSolver()
    cnf = CNF(num_vars=2, clauses=[[1, 2], [-1, 2]])
    res = solver.solve(cnf)
    assert res.status == SatStatus.SAT
    assert res.model is not None
    assert res.model[2] is True


def test_dpll_trivial_unsat() -> None:
    """Kiểm tra CNF đơn giản mâu thuẫn UNSAT: (1) and (-1)."""
    solver = DPLLSolver()
    cnf = CNF(num_vars=1, clauses=[[1], [-1]])
    res = solver.solve(cnf)
    assert res.status == SatStatus.UNSAT
    assert res.model is None


def test_dpll_assumptions() -> None:
    """Kiểm tra khả năng giải với các giả định ban đầu."""
    solver = DPLLSolver()
    # (1 or 2)
    cnf = CNF(num_vars=2, clauses=[[1, 2]])
    # Nếu ép assumption -1 và -2 -> UNSAT
    res = solver.solve(cnf, assumptions=[-1, -2])
    assert res.status == SatStatus.UNSAT


def test_dpll_propagates_units_and_completes_model() -> None:
    """Lan truyền qua nhiều lượt quét và điền cả biến không xuất hiện trong CNF."""
    cnf = CNF(num_vars=4, clauses=[[-2, 3], [-1, 2], [1, 1]])

    res = DPLLSolver().solve(cnf)

    assert res.status == SatStatus.SAT
    assert res.model == {1: True, 2: True, 3: True, 4: False}
    assert res.stats is not None
    assert res.stats.propagations == 3
    assert res.stats.decisions == 0


def test_dpll_backtracks_after_a_conflict() -> None:
    """Quay lui phải hoàn tác các giá trị đã lan truyền trong nhánh thất bại."""
    cnf = CNF(num_vars=3, clauses=[[-1, 2], [-1, -2], [1, 3]])
    original = cnf.copy()

    res = DPLLSolver().solve(cnf)

    assert res.status == SatStatus.SAT
    assert res.model == {1: False, 2: False, 3: True}
    assert res.stats is not None
    assert res.stats.decisions == 2
    assert res.stats.propagations == 2
    assert res.stats.backtracks == 1
    assert cnf == original


def test_dpll_reuses_solver_after_conflicting_assumptions() -> None:
    """Mỗi lần solve giữ assignments và bộ đếm riêng."""
    solver = DPLLSolver()
    cnf = CNF(num_vars=2)

    conflict = solver.solve(cnf, assumptions=[1, -1])
    solved = solver.solve(cnf, assumptions=[-1, 2, 2])

    assert conflict.status == SatStatus.UNSAT
    assert conflict.model is None
    assert solved.status == SatStatus.SAT
    assert solved.model == {1: False, 2: True}
    assert solved.stats is not None
    assert solved.stats.propagations == 0


def test_dpll_empty_formula_and_empty_clause() -> None:
    """CNF không có mệnh đề luôn đúng, còn mệnh đề rỗng luôn sai."""
    solver = DPLLSolver()

    sat = solver.solve(CNF(num_vars=0))
    unsat = solver.solve(CNF(num_vars=0, clauses=[[]]))

    assert sat.status == SatStatus.SAT
    assert sat.model == {}
    assert unsat.status == SatStatus.UNSAT
    assert unsat.model is None


def test_dpll_expired_deadline() -> None:
    """Tôn trọng deadline đã hết hạn ngay cả khi CNF rỗng."""
    res = DPLLSolver().solve(CNF(num_vars=0), deadline=time.perf_counter() - 1.0)

    assert res.status == SatStatus.TIMEOUT
    assert res.model is None
    assert res.stats is not None


def test_dpll_timeout_during_propagation(monkeypatch: pytest.MonkeyPatch) -> None:
    """Dừng giữa lượt giải và trả về cả thống kê đã thu thập."""
    clock = count()
    monkeypatch.setattr(dpll, "time", SimpleNamespace(perf_counter=lambda: float(next(clock))))
    cnf = CNF(num_vars=100, clauses=[[variable] for variable in range(1, 101)])

    res = DPLLSolver().solve(cnf, deadline=20.0)

    assert res.status == SatStatus.TIMEOUT
    assert res.model is None
    assert res.stats is not None
    assert 0 < res.stats.propagations < 100


def _satisfies(clauses: list[list[int]], model: dict[int, bool]) -> bool:
    """Đánh giá trực tiếp CNF trên một model đầy đủ."""
    return all(any(model[abs(literal)] == (literal > 0) for literal in clause) for clause in clauses)


def test_dpll_matches_brute_force() -> None:
    """So sánh kết quả và kiểm tra model trên các công thức nhỏ có seed cố định."""
    random = Random(7)
    solver = DPLLSolver()

    for num_vars in range(1, 7):
        variables = range(1, num_vars + 1)
        literals = [*variables, *range(-num_vars, 0)]
        for _ in range(30):
            clauses = [
                random.choices(literals, k=random.randint(1, 4))
                for _ in range(random.randint(0, 12))
            ]
            assumptions = random.choices(literals, k=random.randint(0, 2))
            required = clauses + [[literal] for literal in assumptions]
            expected_sat = any(
                _satisfies(required, dict(zip(variables, values)))
                for values in product((False, True), repeat=num_vars)
            )

            res = solver.solve(CNF(num_vars, clauses), assumptions)

            assert res.status == (SatStatus.SAT if expected_sat else SatStatus.UNSAT)
            if expected_sat:
                assert res.model is not None
                assert res.model.keys() == set(variables)
                assert _satisfies(required, res.model)
            else:
                assert res.model is None

def run_tests() -> pytest.ExitCode:
    """Chạy các test DPLL trong file này bằng pytest."""
    return pytest.main([__file__, "-v"])


if __name__ == "__main__":
    raise SystemExit(run_tests())