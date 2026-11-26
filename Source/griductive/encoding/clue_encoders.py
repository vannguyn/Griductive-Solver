"""Individual clue encoders and dispatching logic.

Tác dụng:
    Chuyển đổi từng đối tượng Clue cụ thể thành các mệnh đề CNF tương đương:
    - FACT: unit clause [var] hoặc [-var]
    - SAME: (¬A ∨ B) ∧ (A ∨ ¬B)
    - DIFFERENT: (A ∨ B) ∧ (¬A ∨ ¬B)
    - EXACTLY, AT_LEAST, AT_MOST: gọi cardinality.encode_cardinality
    - PARITY: cấm các cấu hình chẵn hoặc lẻ trái quy định
    - COMPOUND: Tseitin transformation hoặc liên kết logic AND/OR/NOT
    - COMPARE_COUNT: so sánh số lượng Criminal giữa 2 vùng qua reified AT_LEAST literals

Input:
    Đối tượng Clue, đối tượng VarMap, và direct_threshold.

Output:
    Danh sách các mệnh đề list[Clause].
    Được gọi bởi Encoder.encode().

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from itertools import product

from griductive.clues.base import Clue
from griductive.clues.core import (
    AtLeastClue,
    AtMostClue,
    DifferentClue,
    ExactlyClue,
    FactClue,
    SameClue,
)
from griductive.clues.extensions import CompareCountClue, CompoundClue, ParityClue
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
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    if clue.parity not in ("EVEN", "ODD"):
        return [[]]
    if not lits:
        return [] if clue.parity == "EVEN" else [[]]
    clauses: list[Clause] = []
    if 2 ** (len(lits) - 1) > direct_threshold:
        result = _parity_literal(clue, varmap, clauses)
        clauses.append([result])
        return clauses

    is_even = (clue.parity == "EVEN")
    for bits in product((False, True), repeat=len(lits)):
        if (sum(bits) % 2 == 0) != is_even:
            clauses.append([-lit if bit else lit for lit, bit in zip(lits, bits)])
    return clauses


def _parity_literal(clue: ParityClue, varmap: VarMap, clauses: list[Clause]) -> int:
    lits = [varmap.coord_to_var(c) for c in clue.region_cells]
    if not lits or clue.parity not in ("EVEN", "ODD"):
        return _and_literal([], varmap, clauses) * (1 if clue.parity == "EVEN" else -1)
    odd = lits[0]
    for lit in lits[1:]:
        result = varmap.allocate_aux_var()
        clauses.extend([
            [-odd, -lit, -result], [odd, lit, -result],
            [-odd, lit, result], [odd, -lit, result],
        ])
        odd = result
    return odd if clue.parity == "ODD" else -odd


def _and_literal(lits: list[int], varmap: VarMap, clauses: list[Clause]) -> int:
    """Return a literal equivalent to the conjunction of lits (AND), including empty AND = True.

    - len == 0: vacuously True -> allocate a fresh aux var forced True with [result].
    - len == 1: return lits[0] directly (no extra variable).
    - len >= 2: Tseitin AND gate.
    """
    if not lits:
        # AND of zero sub-clauses is vacuously True.
        result = varmap.allocate_aux_var()
        clauses.append([result])   # force result = True
        return result
    if len(lits) == 1:
        return lits[0]
    result = varmap.allocate_aux_var()
    clauses.extend([[-result, lit] for lit in lits])
    clauses.append([result, *(-lit for lit in lits)])
    return result


def _at_most_literal(
    lits: list[int], k: int, varmap: VarMap, threshold: int, clauses: list[Clause],
) -> int:
    """Tie a fresh variable to a count bound by encoding both polarities."""
    result = varmap.allocate_aux_var()
    satisfied = encode_cardinality(lits, k, "AT_MOST", varmap, threshold)
    violated = encode_cardinality(lits, k + 1, "AT_LEAST", varmap, threshold)
    clauses.extend([[-result, *clause] for clause in satisfied])
    clauses.extend([[result, *clause] for clause in violated])
    return result


def _clue_literal(
    clue: Clue, varmap: VarMap, threshold: int, clauses: list[Clause],
) -> int:
    if isinstance(clue, CompoundClue):
        if clue.op == "NOT" and len(clue.sub_clues) == 1:
            return -_clue_literal(clue.sub_clues[0], varmap, threshold, clauses)
        if clue.op in ("AND", "OR"):
            children = [_clue_literal(sub, varmap, threshold, clauses) for sub in clue.sub_clues]
            if clue.op == "AND":
                return _and_literal(children, varmap, clauses)
            return -_and_literal([-child for child in children], varmap, clauses)
        return -_and_literal([], varmap, clauses)

    if isinstance(clue, ParityClue):
        return _parity_literal(clue, varmap, clauses)

    if isinstance(clue, (AtMostClue, AtLeastClue, ExactlyClue)):
        lits = [varmap.coord_to_var(c) for c in clue.region_cells]
        if isinstance(clue, AtMostClue):
            return _at_most_literal(lits, clue.k, varmap, threshold, clauses)
        lower = _at_most_literal([-lit for lit in lits], len(lits) - clue.k, varmap, threshold, clauses)
        if isinstance(clue, AtLeastClue):
            return lower
        upper = _at_most_literal(lits, clue.k, varmap, threshold, clauses)
        return _and_literal([lower, upper], varmap, clauses)

    # For FACT, SAME and DIFFERENT, reify the small direct CNF clause by clause.
    direct = encode_single_clue(clue, varmap, threshold)
    clause_lits = [-_and_literal([-lit for lit in clause], varmap, clauses) for clause in direct]
    return _and_literal(clause_lits, varmap, clauses)


def encode_compound(clue: CompoundClue, varmap: VarMap, direct_threshold: int = 64) -> list[Clause]:
    """Mã hóa clue COMPOUND (AND/OR/NOT)."""
    clauses: list[Clause] = []
    result = _clue_literal(clue, varmap, direct_threshold, clauses)
    clauses.append([result])
    return clauses


def _reify_at_least(
    lits: list[int],
    k: int,
    varmap: VarMap,
    clauses: list[Clause],
    direct_threshold: int,
) -> int:
    """Tạo auxiliary literal r sao cho r = True  <=>  sum(lits) >= k.

    Encode hai chiều:
      r -> AT_LEAST(k):  NOT r OR (mỗi clause của AT_LEAST đều thỏa)
      NOT r -> AT_MOST(k-1):  r OR (mỗi clause của AT_MOST(k-1) đều thỏa)
    """
    if k <= 0:
        # sum >= 0 luôn True
        r = varmap.allocate_aux_var()
        clauses.append([r])
        return r
    if k > len(lits):
        # sum >= k > n luôn False
        r = varmap.allocate_aux_var()
        clauses.append([-r])
        return r

    r = varmap.allocate_aux_var()

    # r -> AT_LEAST(k): với mỗi clause c của AT_LEAST(k), thêm (NOT r OR c)
    for c in encode_cardinality(lits, k, "AT_LEAST", varmap, direct_threshold):
        clauses.append([-r] + list(c))

    # NOT r -> AT_MOST(k-1): với mỗi clause c của AT_MOST(k-1), thêm (r OR c)
    for c in encode_cardinality(lits, k - 1, "AT_MOST", varmap, direct_threshold):
        clauses.append([r] + list(c))

    return r


def encode_compare_count(
    clue: CompareCountClue, varmap: VarMap, direct_threshold: int = 64
) -> list[Clause]:
    """Mã hóa clue COMPARE_COUNT: sum(left) op sum(right), op in GREATER/LESS/EQUAL.

    Phương pháp reified AT_LEAST:
      Dùng các literal reified r_L(k) = "sum(left) >= k" và
      r_R(k) = "sum(right) >= k"; k = 0 được dùng cho bất đẳng thức nghiêm ngặt.

      GREATER (left > right):
        <=> For every k in 0..|right|, right >= k implies left >= k+1.
        => clause: [-r_R(k), r_L(k+1)]

      LESS (left < right):
        <=> For every k in 0..|left|, left >= k implies right >= k+1.
        => clause: [-r_L(k), r_R(k+1)]

      EQUAL (left == right):
        <=> For all k: r_L <=> r_R
        => clauses: [r_L, -r_R] AND [-r_L, r_R]
    """
    left_lits = [varmap.coord_to_var(c) for c in clue.region_left_cells]
    right_lits = [varmap.coord_to_var(c) for c in clue.region_right_cells]
    n, m = len(left_lits), len(right_lits)
    op = clue.op  # "GREATER", "LESS", "EQUAL"

    clauses: list[Clause] = []
    max_k = max(n, m)

    if op == "GREATER":
        for k in range(0, m + 1):
            r_right = _reify_at_least(
                right_lits, k, varmap, clauses, direct_threshold
            )
            r_left_next = _reify_at_least(
                left_lits, k + 1, varmap, clauses, direct_threshold
            )
            clauses.append([-r_right, r_left_next])
    elif op == "LESS":
        for k in range(0, n + 1):
            r_left = _reify_at_least(
                left_lits, k, varmap, clauses, direct_threshold
            )
            r_right_next = _reify_at_least(
                right_lits, k + 1, varmap, clauses, direct_threshold
            )
            clauses.append([-r_left, r_right_next])
    elif op == "EQUAL":
        for k in range(1, max_k + 1):
            r_L = _reify_at_least(left_lits, k, varmap, clauses, direct_threshold)
            r_R = _reify_at_least(right_lits, k, varmap, clauses, direct_threshold)
            clauses.append([r_L, -r_R])
            clauses.append([-r_L, r_R])

    return clauses


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
    elif isinstance(clue, CompareCountClue):
        return encode_compare_count(clue, varmap, direct_threshold)
    else:
        raise NotImplementedError(f"Chưa hỗ trợ encoder cho loại clue: {clue.clue_type}")
