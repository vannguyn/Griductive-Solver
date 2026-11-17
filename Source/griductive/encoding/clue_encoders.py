"""Individual clue encoders and dispatching logic.

Tác dụng:
    Chuyển đổi từng đối tượng Clue cụ thể thành các mệnh đề CNF tương đương:
    - FACT: unit clause [var] hoặc [-var]
    - SAME: (¬A ∨ B) ∧ (A ∨ ¬B)
    - DIFFERENT: (A ∨ B) ∧ (¬A ∨ ¬B)
    - EXACTLY, AT_LEAST, AT_MOST: gọi cardinality.encode_cardinality
    - PARITY: cấm các cấu hình chẵn hoặc lẻ trái quy định
    - COMPOUND: Tseitin transformation hoặc liên kết logic AND/OR/NOT

Input:
    Đối tượng Clue, đối tượng VarMap, và direct_threshold.

Output:
    Danh sách các mệnh đề list[Clause].
    Được gọi bởi Encoder.encode().

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

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
from griductive.domain.types import Status
from griductive.encoding.cardinality import encode_cardinality
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import Clause


def encode_fact(clue: FactClue, varmap: VarMap) -> list[Clause]:
    """Mã hóa clue FACT: gán C_i = True (Criminal) hoặc C_i = False (Innocent)."""
    var = varmap.coord_to_var(clue.target_cell)
    lit = var if clue.target_status == Status.CRIMINAL else -var
    return [[lit]]


def encode_same(clue: SameClue, varmap: VarMap) -> list[Clause]:
    """Mã hóa clue SAME: C_a <=> C_b  =>  (¬A ∨ B) ∧ (A ∨ ¬B)."""
    a = varmap.coord_to_var(clue.cell_a)
    b = varmap.coord_to_var(clue.cell_b)
    return [[-a, b], [a, -b]]


def encode_different(clue: DifferentClue, varmap: VarMap) -> list[Clause]:
    """Mã hóa clue DIFFERENT: C_a XOR C_b  =>  (A ∨ B) ∧ (¬A ∨ ¬B)."""
    a = varmap.coord_to_var(clue.cell_a)
    b = varmap.coord_to_var(clue.cell_b)
    return [[a, b], [-a, -b]]


def encode_exactly(clue: ExactlyClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue EXACTLY qua bộ đếm cardinality."""
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    return encode_cardinality(lits, clue.k, "EXACTLY", varmap, direct_threshold)


def encode_at_least(clue: AtLeastClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue AT_LEAST qua bộ đếm cardinality."""
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    return encode_cardinality(lits, clue.k, "AT_LEAST", varmap, direct_threshold)


def encode_at_most(clue: AtMostClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue AT_MOST qua bộ đếm cardinality."""
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    return encode_cardinality(lits, clue.k, "AT_MOST", varmap, direct_threshold)


def encode_parity(clue: ParityClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue PARITY (EVEN hoặc ODD)."""
    import itertools
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    clauses: list[Clause] = []
    # Với vùng nhỏ, cấm mọi phép gán có parity trái ngược
    is_even = (clue.parity == "EVEN")
    for bits in itertools.product([0, 1], repeat=len(lits)):
        count_ones = sum(bits)
        # Nếu parity của tổ hợp này sai -> thêm mệnh đề cấm
        if (count_ones % 2 == 0) != is_even:
            clause = [-lit if b == 1 else lit for lit, b in zip(lits, bits)]
            clauses.append(clause)
    return clauses


def encode_compound(clue: CompoundClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue COMPOUND (AND/OR/NOT)."""
    # TODO (Nhật Tân): Hoàn thiện biến phụ Tseitin cho Compound Clue
    raise NotImplementedError("Nhật Tân sẽ hoàn thiện mã hóa Compound Clue tại đây.")


def encode_single_clue(
    clue: Clue,
    varmap: VarMap,
    direct_threshold: int = 64,
) -> list[Clause]:
    """Dispatcher: Tự động điều hướng và mã hóa đối tượng Clue bất kỳ."""
    if isinstance(clue, FactClue):
        return encode_fact(clue, varmap)
    elif isinstance(clue, SameClue):
        return encode_same(clue, varmap)
    elif isinstance(clue, DifferentClue):
        return encode_different(clue, varmap)
    elif isinstance(clue, ExactlyClue):
        return encode_exactly(clue, varmap, direct_threshold)
    elif isinstance(clue, AtLeastClue):
        return encode_at_least(clue, varmap, direct_threshold)
    elif isinstance(clue, AtMostClue):
        return encode_at_most(clue, varmap, direct_threshold)
    elif isinstance(clue, ParityClue):
        return encode_parity(clue, varmap, direct_threshold)
    elif isinstance(clue, CompoundClue):
        return encode_compound(clue, varmap, direct_threshold)
    else:
        raise NotImplementedError(f"Chưa hỗ trợ encoder cho loại clue: {clue.clue_type}")
