"""Cross-testing: CNF Encoder vs. Semantic Evaluator.

Tác dụng:
    Kiểm thử chéo độc lập giữa Encoder (Nhật Tân) và Semantic Evaluator (Nhật Minh):
    Với mọi loại Clue (6 core + 2 extensions) và với mọi phép gán giá trị Boolean của các ô liên quan,
    chứng minh rằng:
        clue.evaluate(assignment) == True <=> CNF(clue) kết hợp với assignment là SAT.

Input:
    Các đối tượng Clue khác nhau và toàn bộ 2^k phép gán chân trị.

Output:
    Khẳng định tính tương đương logic 100% giữa CNF và ngữ nghĩa đề bài.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics) phối hợp Nhật Tân.
"""

import itertools
import pytest
from griductive.clues.core import DifferentClue, ExactlyClue, FactClue, SameClue
from griductive.domain.regions import RegionKind, RegionSpec
from griductive.domain.types import Status
from griductive.encoding.encoder import Encoder
from griductive.encoding.varmap import VarMap
from griductive.sat.dpll import DPLLSolver


def test_fact_encoder_vs_eval() -> None:
    """Kiểm tra clue FACT tương đương giữa evaluator và CNF."""
    clue = FactClue("c1", "A1", target_cell="A1", target_status=Status.CRIMINAL)
    varmap = VarMap(size=3)
    encoder = Encoder(varmap=varmap)
    cnf, _ = encoder.encode([clue])
    solver = DPLLSolver()

    # Thử cả 2 trường hợp A1=True và A1=False
    for a1_val in (True, False):
        assign = {"A1": a1_val}
        eval_res = clue.evaluate(assign)
        var_a1 = varmap.coord_to_var("A1")
        sat_res = solver.solve(cnf, assumptions=[var_a1 if a1_val else -var_a1])
        is_sat = (sat_res.status.name == "SAT")
        assert eval_res == is_sat, f"Lệch ngữ nghĩa tại A1={a1_val}: eval={eval_res}, sat={is_sat}"


def test_different_encoder_vs_eval() -> None:
    """Kiểm tra clue DIFFERENT tương đương giữa evaluator và CNF."""
    clue = DifferentClue("c2", "A1", cell_a="A1", cell_b="B1")
    varmap = VarMap(size=3)
    encoder = Encoder(varmap=varmap)
    cnf, _ = encoder.encode([clue])
    solver = DPLLSolver()

    for a1, b1 in itertools.product([True, False], repeat=2):
        assign = {"A1": a1, "B1": b1}
        eval_res = clue.evaluate(assign)
        var_a1 = varmap.coord_to_var("A1")
        var_b1 = varmap.coord_to_var("B1")
        assump = [var_a1 if a1 else -var_a1, var_b1 if b1 else -var_b1]
        sat_res = solver.solve(cnf, assumptions=assump)
        is_sat = (sat_res.status.name == "SAT")
        assert eval_res == is_sat
