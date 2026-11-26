"""Unit tests for Uniqueness Check.

Tác dụng:
    Kiểm thử hàm check_uniqueness() phân biệt chính xác 4 trường hợp:
    UNIQUE, MULTIPLE, UNSAT, và TIMEOUT.
    Bảo đảm chỉ chặn các biến chính (1..num_primary_vars), không bị ảnh hưởng sai bởi biến phụ.

Input:
    CNF có 1 nghiệm, nhiều nghiệm, vô nghiệm, hoặc solver giả lập timeout.

Output:
    Khẳng định tính đúng đắn của UniquenessResult.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

import time
from unittest.mock import call, create_autospec

import pytest

from griductive.domain.types import UniquenessResult
from griductive.reasoning.uniqueness import check_uniqueness
from griductive.sat.cnf import CNF, SatResult, SatStatus
from griductive.sat.dpll import DPLLSolver
from griductive.sat.solver import SatSolver
from griductive.sat.stats import SolverStats


def test_uniqueness_single_solution() -> None:
    """Công thức ép nghiệm duy nhất: var 1 = True, var 2 = False."""
    cnf = CNF(num_vars=2, clauses=[[1], [-2]])
    res = check_uniqueness(cnf, num_primary_vars=2, solver=DPLLSolver())
    assert res.result == UniquenessResult.UNIQUE
    assert res.first_model == {1: True, 2: False}


def test_uniqueness_multiple_solutions() -> None:
    """Công thức có nhiều nghiệm: (1 or 2) có 3 nghiệm."""
    cnf = CNF(num_vars=2, clauses=[[1, 2]])
    res = check_uniqueness(cnf, num_primary_vars=2, solver=DPLLSolver())
    assert res.result == UniquenessResult.MULTIPLE


def test_uniqueness_unsat() -> None:
    """Công thức mâu thuẫn ngay từ đầu."""
    cnf = CNF(num_vars=1, clauses=[[1], [-1]])
    res = check_uniqueness(cnf, num_primary_vars=1, solver=DPLLSolver())
    assert res.result == UniquenessResult.UNSAT


def test_uniqueness_ignores_alternative_auxiliary_assignments() -> None:
    """Hai nghiệm chỉ khác biến phụ vẫn là một nghiệm trên bàn cờ."""
    cnf = CNF(num_vars=4, clauses=[[1], [-2], [3, 4], [-3, -4]])
    solver = DPLLSolver()
    original = cnf.copy()

    assert solver.solve(cnf, assumptions=[3]).status == SatStatus.SAT
    assert solver.solve(cnf, assumptions=[-3]).status == SatStatus.SAT

    res = check_uniqueness(cnf, num_primary_vars=2, solver=solver)

    assert res.result == UniquenessResult.UNIQUE
    assert res.first_model is not None
    assert res.first_model[1] is True
    assert res.first_model[2] is False
    assert cnf == original


def test_uniqueness_timeout_before_first_model() -> None:
    """Deadline đã hết thì không thể kết luận puzzle vô nghiệm."""
    res = check_uniqueness(
        CNF(num_vars=1, clauses=[[1]]),
        num_primary_vars=1,
        solver=DPLLSolver(),
        deadline=time.perf_counter() - 1.0,
    )

    assert res.result == UniquenessResult.TIMEOUT
    assert res.first_model is None
    assert res.stats is not None


def test_uniqueness_timeout_after_first_model() -> None:
    """Truy vấn thứ hai dùng cùng deadline và giữ model đầu tiên nếu quá hạn."""
    cnf = CNF(num_vars=3, clauses=[[1], [-2]])
    first = DPLLSolver().solve(cnf)
    timeout_stats = SolverStats(runtime_ms=1.0)
    solver = create_autospec(SatSolver, instance=True)
    solver.solve.side_effect = [first, SatResult(SatStatus.TIMEOUT, stats=timeout_stats)]
    deadline = 42.0

    res = check_uniqueness(cnf, num_primary_vars=2, solver=solver, deadline=deadline)

    assert res.result == UniquenessResult.TIMEOUT
    assert res.first_model == first.model
    assert res.stats == timeout_stats
    assert solver.solve.call_args_list == [
        call(cnf, assumptions=(), deadline=deadline),
        call(CNF(num_vars=3, clauses=[[1], [-2], [-1, 2]]), assumptions=(), deadline=deadline),
    ]


def run_tests() -> pytest.ExitCode:
    """Chạy các test kiểm tra nghiệm duy nhất trong file này."""
    return pytest.main([__file__, "-v"])


if __name__ == "__main__":
    raise SystemExit(run_tests())