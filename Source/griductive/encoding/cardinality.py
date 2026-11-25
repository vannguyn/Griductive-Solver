"""Cardinality constraint encoders (AtLeast, AtMost, Exactly).

Tác dụng:
    Mã hóa các ràng buộc đếm số lượng (Cardinality Constraints) sang CNF:
    - sum(lits) <= k (AT_MOST)
    - sum(lits) >= k (AT_LEAST)
    - sum(lits) == k (EXACTLY)
    Tự động ước lượng số lượng clause:
    - Nếu số clause ước tính <= direct_threshold (mặc định 64): Dùng mã hóa tổ hợp trực tiếp (Direct/Combinatorial Encoding, không cần biến phụ).
    - Nếu vượt quá ngưỡng: Tự động chuyển sang Sequential Counter (Sinz, 2005) dùng biến phụ để tránh bùng nổ số lượng mệnh đề O(2^N).

Input:
    Danh sách literal (lits: Sequence[int]), ngưỡng k, loại ràng buộc (kind), đối tượng VarMap, và direct_threshold.

Output:
    Danh sách các mệnh đề list[Clause] bổ sung vào CNF.
    Được clue_encoders sử dụng.

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

import math
from collections.abc import Sequence
from griductive.encoding.varmap import VarMap
from griductive.sat.cnf import Clause


def estimate_direct_clauses(n: int, k: int, kind: str) -> int:
    """Ước lượng số lượng mệnh đề nếu dùng tổ hợp trực tiếp C(n, k+1) hoặc C(n, n-k+1)."""
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
    """Mã hóa sum(lits) <= k bằng cách cấm mọi tập con cỡ k+1 literal cùng True."""
    import itertools
    clauses: list[Clause] = []
    n = len(lits)
    if k < 0:
        # Không thể có <= âm -> mệnh đề rỗng (UNSAT)
        return [[]]
    if k >= n:
        return []  # Luôn thỏa mãn
    for subset in itertools.combinations(lits, k + 1):
        clauses.append([-lit for lit in subset])
    return clauses


def encode_at_least_direct(lits: Sequence[int], k: int) -> list[Clause]:
    """Mã hóa sum(lits) >= k bằng cách cấm mọi tập con cỡ n-k+1 literal cùng False."""
    import itertools
    clauses: list[Clause] = []
    n = len(lits)
    if k <= 0:
        return []  # Luôn thỏa mãn
    if k > n:
        return [[]]  # Không thể có >= k > n -> UNSAT
    for subset in itertools.combinations(lits, n - k + 1):
        clauses.append([lit for lit in subset])
    return clauses


def encode_sequential_counter(
    lits: Sequence[int],
    k: int,
    kind: str,
    varmap: VarMap,
) -> list[Clause]:
    """Mã hóa ràng buộc cardinality bằng Sequential Counter (Sinz 2005) dùng biến phụ."""
    # TODO (Nhật Tân): Cài đặt Sequential Counter cho vùng lớn
    # Với lưới 3x3 và 4x4, direct encoding đã đủ đáp ứng hầu hết trường hợp <= 64 clauses.
    # Sequential counter sẽ giải quyết triệt để stress-case 5x5.
    raise NotImplementedError("Nhật Tân sẽ hoàn thiện Sequential Counter fallback tại đây.")


def encode_cardinality(
    lits: Sequence[int],
    k: int,
    kind: str,
    varmap: VarMap,
    direct_threshold: int = 64,
) -> list[Clause]:
    """Mã hóa tổng quát ràng buộc đếm số lượng sang CNF."""
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
