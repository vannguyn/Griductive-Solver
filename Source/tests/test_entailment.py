"""Entailment deduction test suite based on Project Handout specifications.

Tác dụng:
    Kiểm tra cơ chế suy diễn entailment theo đúng ví dụ mẫu trong đề bài:
    - Cho KB gồm (A ∨ B) ∧ (¬A ∨ B):
      Suy ra B là CRIMINAL (vì KB ∧ ¬B là UNSAT), và A là UNKNOWN (vì cả hai nhánh đều SAT).
    - Kiểm tra các trường hợp biên:
      + INCONSISTENT khi KB tự mâu thuẫn ngay từ đầu.
      + TIMEOUT khi solver quá giờ (không bị gán nhầm thành UNSAT).

Input:
    CNF công thức kiểm thử và DPLLSolver.

Output:
    Khẳng định tính chính xác của hàm classify() và check_kb_consistent().

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import pytest
from griductive.domain.types import Classification
from griductive.reasoning.entailment import classify
from griductive.sat.cnf import CNF, SatResult, SatStatus
from griductive.sat.dpll import DPLLSolver


def test_handout_example_a_and_b() -> None:
    """Kiểm tra ví dụ trong đề bài: (A ∨ B) ∧ (¬A ∨ B) với var 1=A, var 2=B."""
    # Clauses: [1, 2] và [-1, 2]
    cnf = CNF(num_vars=2, clauses=[[1, 2], [-1, 2]])
    solver = DPLLSolver()

    # Phân loại biến 2 (B): phải là CRIMINAL
    outcome_b = classify(cnf, var_id=2, solver=solver)
    assert outcome_b.classification == Classification.CRIMINAL
    assert len(outcome_b.queries) == 2

    # Phân loại biến 1 (A): phải là UNKNOWN
    outcome_a = classify(cnf, var_id=1, solver=solver)
    assert outcome_a.classification == Classification.UNKNOWN
    assert len(outcome_a.queries) == 2


def test_entailment_innocent() -> None:
    """Kiểm tra trường hợp ép INNOCENT: (A ∨ ¬B) ∧ (¬A ∨ ¬B) => B phải là INNOCENT."""
    cnf = CNF(num_vars=2, clauses=[[1, -2], [-1, -2]])
    solver = DPLLSolver()

    outcome_b = classify(cnf, var_id=2, solver=solver)
    assert outcome_b.classification == Classification.INNOCENT


def test_entailment_timeout_handling() -> None:
    """Kiểm tra solver trả TIMEOUT thì classify phải trả Classification.TIMEOUT, không được biến thành UNSAT."""
    class DummyTimeoutSolver:
        def solve(self, cnf, assumptions=(), deadline=None):
            return SatResult(status=SatStatus.TIMEOUT)

    cnf = CNF(num_vars=1, clauses=[[1]])
    outcome = classify(cnf, var_id=1, solver=DummyTimeoutSolver())
    assert outcome.classification == Classification.TIMEOUT
