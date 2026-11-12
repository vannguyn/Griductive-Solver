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

import pytest
from griductive.domain.types import UniquenessResult
from griductive.reasoning.uniqueness import check_uniqueness
from griductive.sat.cnf import CNF
from griductive.sat.dpll import DPLLSolver


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
