from itertools import product

import pytest

from griductive.clues.base import Clue
from griductive.clues.core import (
    AtLeastClue,
    AtMostClue,
    DifferentClue,
    ExactlyClue,
    FactClue,
    SameClue,
)
from griductive.clues.extensions import CompoundClue, ParityClue
from griductive.domain.grid import all_coords
from griductive.domain.regions import RegionKind, RegionSpec
from griductive.domain.types import Status
from griductive.encoding.encoder import Encoder
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import SatStatus
from griductive.sat.dpll import DPLLSolver


ROW = RegionSpec(kind=RegionKind.ROW, index=1)
ROW_CELLS = ("A1", "B1", "C1")
FACT_A = FactClue("a", "A1", "A1", Status.CRIMINAL)
FACT_B = FactClue("b", "A1", "B1", Status.CRIMINAL)
NOT_A = CompoundClue("not-a", "A1", "NOT", (FACT_A,))
AND_AB = CompoundClue("and", "A1", "AND", (FACT_A, FACT_B))
OR_NOT_A_B = CompoundClue("or", "A1", "OR", (NOT_A, FACT_B))
COMPOUND_CASES = (
    pytest.param(AND_AB, (False, False, False, True), id="AND"),
    pytest.param(OR_NOT_A_B, (True, True, False, True), id="OR-with-NOT"),
    pytest.param(NOT_A, (True, True, False, False), id="NOT"),
)
CARDINALITY_CASES = (
    pytest.param(ExactlyClue("exactly", "A1", 1, ROW, ROW_CELLS), id="EXACTLY"),
    pytest.param(AtLeastClue("at-least", "A1", 2, ROW, ROW_CELLS), id="AT_LEAST"),
    pytest.param(AtMostClue("at-most", "A1", 1, ROW, ROW_CELLS), id="AT_MOST"),
)


def _assert_encoder_matches_evaluator(clue: Clue, direct_threshold: int = 64) -> None:
    """Đối chiếu trên mọi phép gán biến chính và để solver tự gán biến phụ."""
    varmap = VarMap(size=3)
    encoder = Encoder(varmap=varmap, direct_threshold=direct_threshold)
    cnf, _ = encoder.encode([clue])
    solver = DPLLSolver()
    coords = all_coords(varmap.size)
    variables = [varmap.coord_to_var(coord) for coord in coords]

    for values in product((False, True), repeat=len(coords)):
        assignment = dict(zip(coords, values))
        assumptions = [var if value else -var for var, value in zip(variables, values)]
        expected = SatStatus.SAT if clue.evaluate(assignment) else SatStatus.UNSAT

        result = solver.solve(cnf, assumptions=assumptions)

        assert result.status == expected, f"{clue!r} lệch tại {assignment}"


@pytest.mark.parametrize("clue", (
    pytest.param(FACT_A, id="FACT-criminal"),
    pytest.param(FactClue("innocent", "A1", "A1", Status.INNOCENT), id="FACT-innocent"),
    pytest.param(SameClue("same", "A1", "A1", "B1"), id="SAME"),
    pytest.param(DifferentClue("different", "A1", "A1", "B1"), id="DIFFERENT"),
    *CARDINALITY_CASES,
    pytest.param(ParityClue("even", "A1", "EVEN", ROW, ROW_CELLS), id="PARITY-even"),
    pytest.param(ParityClue("odd", "A1", "ODD", ROW, ROW_CELLS), id="PARITY-odd"),
))
def test_direct_encoder_vs_eval(clue: Clue) -> None:
    """Kiểm tra sáu loại manh mối cốt lõi và PARITY qua encoder trực tiếp."""
    _assert_encoder_matches_evaluator(clue)


@pytest.mark.xfail(raises=NotImplementedError, reason="Sequential Counter đang chờ triển khai")
@pytest.mark.parametrize("clue", CARDINALITY_CASES)
def test_sequential_counter_vs_eval(clue: Clue) -> None:
    """Ép encoder đi qua nhánh Sequential Counter."""
    _assert_encoder_matches_evaluator(clue, direct_threshold=0)


@pytest.mark.parametrize(("clue", "expected"), COMPOUND_CASES)
def test_compound_evaluate(clue: CompoundClue, expected: tuple[bool, ...]) -> None:
    """Đối chiếu evaluate() với bảng chân trị của AND, OR và NOT."""
    assignments = product((False, True), repeat=2)
    actual = tuple(clue.evaluate({"A1": a, "B1": b}) for a, b in assignments)
    assert actual == expected


@pytest.mark.xfail(raises=NotImplementedError, reason="Encoder COMPOUND đang chờ triển khai")
@pytest.mark.parametrize("clue", (
    pytest.param(AND_AB, id="AND"),
    pytest.param(OR_NOT_A_B, id="OR-with-NOT"),
    pytest.param(NOT_A, id="NOT"),
))
def test_compound_encoder_vs_eval(clue: CompoundClue) -> None:
    """Đối chiếu CNF với ngữ nghĩa của manh mối kết hợp."""
    _assert_encoder_matches_evaluator(clue)


def run_tests() -> pytest.ExitCode:
    """Chạy các test đối chiếu encoder trong file này."""
    return pytest.main([__file__, "-v", "-rx"])


if __name__ == "__main__":
    raise SystemExit(run_tests())