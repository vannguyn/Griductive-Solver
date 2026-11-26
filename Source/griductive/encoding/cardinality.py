import math
from collections.abc import Sequence
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import Clause


def estimate_direct_clauses(n: int, k: int, kind: str) -> int:
    kind = kind.upper()
    if kind == "AT_MOST":
        return math.comb(n, k + 1) if 0 <= k < n else 0
    elif kind == "AT_LEAST":
        return math.comb(n, n - k + 1) if 0 < k <= n else 0
    elif kind == "EXACTLY":
        c_most = math.comb(n, k + 1) if 0 <= k < n else 0
        c_least = math.comb(n, n - k + 1) if 0 < k <= n else 0
        return c_most + c_least
    return 0


def encode_at_most_direct(lits: Sequence[int], k: int) -> list[Clause]:
    import itertools
    clauses: list[Clause] = []
    n = len(lits)
    if k < 0:
        return [[]]
    if k >= n:
        return []
    for subset in itertools.combinations(lits, k + 1):
        clauses.append([-lit for lit in subset])
    return clauses


def encode_at_least_direct(lits: Sequence[int], k: int) -> list[Clause]:
    import itertools
    clauses: list[Clause] = []
    n = len(lits)
    if k <= 0:
        return []
    if k > n:
        return [[]]
    for subset in itertools.combinations(lits, n - k + 1):
        clauses.append([lit for lit in subset])
    return clauses


def encode_sequential_counter(
    lits: Sequence[int],
    k: int,
    kind: str,
    varmap: VarMap,
) -> list[Clause]:
    kind = kind.upper()
    if kind == "AT_MOST":
        return _sequential_at_most(lits, k, varmap)
    if kind == "AT_LEAST":
        return _sequential_at_most([-lit for lit in lits], len(lits) - k, varmap)
    if kind == "EXACTLY":
        if not 0 <= k <= len(lits):
            return [[]]
        return encode_sequential_counter(lits, k, "AT_MOST", varmap) + (
            encode_sequential_counter(lits, k, "AT_LEAST", varmap)
        )
    raise ValueError(f"Loại cardinality không hợp lệ: {kind}")


def _sequential_at_most(lits: Sequence[int], k: int, varmap: VarMap) -> list[Clause]:
    if k <= 0 or k >= len(lits):
        return encode_at_most_direct(lits, k)

    clauses: list[Clause] = []
    previous: tuple[int, ...] = ()
    for index, lit in enumerate(lits):
        if len(previous) == k:
            clauses.append([-lit, -previous[-1]])
        if index == len(lits) - 1:
            break
        current = varmap.allocate_aux_vars(min(index + 1, k))
        clauses.append([-lit, current[0]])
        for count_index, prefix_lit in enumerate(previous):
            clauses.append([-prefix_lit, current[count_index]])
            if count_index + 1 < len(current):
                clauses.append([-lit, -prefix_lit, current[count_index + 1]])
        previous = current
    return clauses


def encode_cardinality(
    lits: Sequence[int],
    k: int,
    kind: str,
    varmap: VarMap,
    direct_threshold: int = 64,
) -> list[Clause]:
    kind = kind.upper()
    n = len(lits)
    est = estimate_direct_clauses(n, k, kind)

    if est <= direct_threshold:
        if kind == "AT_MOST":
            return encode_at_most_direct(lits, k)
        elif kind == "AT_LEAST":
            return encode_at_least_direct(lits, k)
        elif kind == "EXACTLY":
            return encode_at_most_direct(lits, k) + encode_at_least_direct(lits, k)
        else:
            raise ValueError(f"Loại cardinality không hợp lệ: {kind}")
    else:
        return encode_sequential_counter(lits, k, kind, varmap)
