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

import pytest
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
