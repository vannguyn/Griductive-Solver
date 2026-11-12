"""Region specifications and cell resolution.

Tác dụng:
    Định nghĩa cấu trúc mô tả vùng (RegionSpec) và hàm giải nghĩa vùng (resolve_region)
    thành danh sách các tọa độ ô cụ thể trên lưới N x N. Hỗ trợ: hàng (row), cột (column),
    8 ô hàng xóm lân cận (neighbors, không tính tâm), và danh sách ô tường minh (explicit).

Input:
    Đối tượng RegionSpec và kích thước lưới size.

Output:
    Tuple[Coord, ...] không trùng lặp, nằm hoàn toàn trong biên của lưới.
    Được dùng bởi clues (core, extensions), encoding (cardinality), và GUI highlight.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

from dataclasses import dataclass
from griductive.domain.errors import InvalidClueError
from griductive.domain.grid import Coord, format_coord, parse_coord, validate_coord
from griductive.domain.types import RegionKind


@dataclass(frozen=True)
class RegionSpec:
    """Mô tả trừu tượng về một vùng trên lưới bàn cờ.

    Attributes:
        kind: Loại vùng (ROW, COLUMN, NEIGHBORS, EXPLICIT).
        index: Chỉ số hàng hoặc cột (1-indexed theo quy ước đề bài: hàng 1..N, cột 1..N).
        center: Tọa độ ô trung tâm nếu kind là NEIGHBORS.
        cells: Danh sách ô cụ thể nếu kind là EXPLICIT.
    """
    kind: RegionKind
    index: int | None = None
    center: Coord | None = None
    cells: tuple[Coord, ...] = ()


def resolve_region(spec: RegionSpec, size: int) -> tuple[Coord, ...]:
    """Phân giải một RegionSpec thành tuple các tọa độ Coord thực tế trong lưới N x N.

    Args:
        spec: Cấu hình vùng cần phân giải.
        size: Kích thước lưới N.

    Returns:
        tuple[Coord, ...]: Danh sách tọa độ hợp lệ, không trùng lặp.

    Raises:
        InvalidClueError: Nếu spec thiếu thông tin hoặc chỉ số nằm ngoài lưới.
    """
    if spec.kind == RegionKind.ROW:
        if spec.index is None or not (1 <= spec.index <= size):
            raise InvalidClueError(f"Chỉ số hàng không hợp lệ: {spec.index} cho lưới {size}x{size}")
        row_idx = spec.index - 1
        return tuple(format_coord(c, row_idx) for c in range(size))

    elif spec.kind == RegionKind.COLUMN:
        if spec.index is None or not (1 <= spec.index <= size):
            raise InvalidClueError(f"Chỉ số cột không hợp lệ: {spec.index} cho lưới {size}x{size}")
        col_idx = spec.index - 1
        return tuple(format_coord(col_idx, r) for r in range(size))

    elif spec.kind == RegionKind.NEIGHBORS:
        if spec.center is None or not validate_coord(spec.center, size):
            raise InvalidClueError(f"Tâm hàng xóm không hợp lệ: {spec.center} cho lưới {size}x{size}")
        c_col, c_row = parse_coord(spec.center)
        neighbors: list[Coord] = []
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = c_row + dr, c_col + dc
                if 0 <= nr < size and 0 <= nc < size:
                    neighbors.append(format_coord(nc, nr))
        return tuple(neighbors)

    elif spec.kind == RegionKind.EXPLICIT:
        if not spec.cells:
            raise InvalidClueError("Vùng explicit không được để rỗng")
        seen: set[Coord] = set()
        resolved: list[Coord] = []
        for c in spec.cells:
            if not validate_coord(c, size):
                raise InvalidClueError(f"Tọa độ explicit {c} nằm ngoài lưới {size}x{size}")
            if c not in seen:
                seen.add(c)
                resolved.append(c)
        return tuple(resolved)

    else:
        raise InvalidClueError(f"Loại vùng không được hỗ trợ: {spec.kind}")
