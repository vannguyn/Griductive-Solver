from itertools import product

import pytest

from griductive.clues.parser import parse_clue
from griductive.domain.grid import all_coords
from griductive.encoding import Encoder, VarMap
from griductive.sat.cnf import SatStatus
from griductive.sat.dpll import DPLLSolver


def _raw(clue_type, **fields):
    return {"id": clue_type, "owner": "A1", "type": clue_type, **fields}


REGION = {"kind": "row", "index": 1}
COUNT_CLUES = [
    _raw(kind, k=k, region=REGION)
    for kind in ("AT_MOST", "AT_LEAST", "EXACTLY")
    for k in range(4)
]
ODD = _raw("PARITY", parity="ODD", region=REGION)
SAME = _raw("SAME", cell_a="A1", cell_b="B1")
DIFFERENT = _raw("DIFFERENT", cell_a="B1", cell_b="C1")
FACT = _raw("FACT", target_cell="C1", status="INNOCENT")
NESTED = _raw(
    "COMPOUND", op="OR", sub_clues=[
        _raw("COMPOUND", op="NOT", sub_clues=[_raw("EXACTLY", k=2, region=REGION)]),
        _raw("COMPOUND", op="AND", sub_clues=[ODD, SAME, DIFFERENT, FACT]),
    ],
)


@pytest.mark.parametrize("op", ["GREATER", "LESS", "EQUAL"])
@pytest.mark.parametrize("threshold", [0, 64])
def test_compare_count_encoding_matches_evaluator(op, threshold):
    raw = _raw(
        "COMPARE_COUNT",
        op=op,
        region_left={"kind": "explicit", "cells": ["A1", "B1"]},
        region_right={"kind": "explicit", "cells": ["A2", "B2", "C2"]},
    )
    clue = parse_clue(raw, 3)
    varmap = VarMap(3)
    cnf, _ = Encoder(varmap, direct_threshold=threshold).encode([clue])
    solver = DPLLSolver()

    for values in product((False, True), repeat=len(clue.cells())):
        assignment = dict(zip(clue.cells(), values))
        assumptions = [
            varmap.coord_to_var(cell) * (1 if value else -1)
            for cell, value in assignment.items()
        ]
        expected = SatStatus.SAT if clue.evaluate(assignment) else SatStatus.UNSAT
        assert solver.solve(cnf, assumptions=assumptions).status == expected


@pytest.mark.parametrize("threshold", [0, 64])
@pytest.mark.parametrize(
    "raw",
    [
        *COUNT_CLUES, ODD, _raw("PARITY", parity="EVEN", region=REGION), NESTED,
        *(_raw("COMPOUND", op="NOT", sub_clues=[child]) for child in [*COUNT_CLUES, ODD, NESTED]),
    ],
)
def test_encoding_matches_evaluator(raw, threshold):
    clue = parse_clue(raw, 3)
    varmap = VarMap(3)
    cnf, stats = Encoder(varmap, direct_threshold=threshold).encode([clue])
    solver = DPLLSolver()
    assert stats.total_vars == cnf.num_vars
    assert stats.clauses == len(cnf.clauses)
    for values in product((False, True), repeat=len(clue.cells())):
        assignment = dict(zip(clue.cells(), values))
        assumptions = [varmap.coord_to_var(cell) * (1 if value else -1)
                       for cell, value in assignment.items()]
        expected = SatStatus.SAT if clue.evaluate(assignment) else SatStatus.UNSAT
        assert solver.solve(cnf, assumptions=assumptions).status == expected


def test_large_regions_use_auxiliary_variables():
    cells = all_coords(5)
    region = {"kind": "explicit", "cells": cells}
    clues = [
        parse_clue(_raw("EXACTLY", k=12, region=region), 5),
        parse_clue(_raw("PARITY", parity="EVEN", region=region), 5),
    ]
    varmap = VarMap(5)
    cnf, stats = Encoder(varmap).encode(clues)
    assert stats.primary_vars == 25
    assert stats.aux_vars > 24
    assert stats.clauses < 2000
    assert max(abs(lit) for clause in cnf.clauses for lit in clause) == cnf.num_vars
    solver = DPLLSolver()
    for count, expected in ((11, SatStatus.UNSAT), (12, SatStatus.SAT), (13, SatStatus.UNSAT)):
        assumptions = [var if var <= count else -var for var in range(1, 26)]
        assert solver.solve(cnf, assumptions=assumptions).status == expected
