"""Coordinate system and grid navigation utilities.

Tác dụng:
    Định nghĩa kiểu tọa độ chuẩn (Coord: chuỗi "A1", "B2", "C3"...) và các hàm chuyển đổi
    giữa tọa độ chữ-số, chỉ số hàng-cột (0-indexed) và chỉ số phẳng row-major (1-indexed cho SAT variable).

Input:
    Chuỗi tọa độ, kích thước lưới N in {3, 4, 5}, chỉ số row/column.

Output:
    Tuple (col_idx, row_idx), chuỗi Coord hợp lệ, danh sách tất cả các ô trong lưới N x N,
    hoặc chỉ số ánh xạ biến row-major.
    Được dùng bởi regions, varmap, loader, engine, board_view, logic_agent.

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

from typing import TypeAlias
from griductive.domain.errors import InvalidCoordError

Coord: TypeAlias = str  # Ví dụ: "A1", "B2", "C3"


def parse_coord(coord: Coord) -> tuple[int, int]:
    """Phân tích chuỗi tọa độ thành cặp chỉ số (col_idx, row_idx) 0-indexed.

    Args:
        coord: Chuỗi tọa độ dạng 'A1', 'B2', ...

    Returns:
        tuple[int, int]: (cột, hàng) bắt đầu từ 0. Ví dụ: 'A1' -> (0, 0), 'B3' -> (1, 2).

    Raises:
        InvalidCoordError: Nếu chuỗi không đúng định dạng.
    """
    if not isinstance(coord, str) or len(coord) < 2:
        raise InvalidCoordError(f"Tọa độ không hợp lệ: {coord!r}")
    col_char = coord[0].upper()
    if not ('A' <= col_char <= 'Z'):
        raise InvalidCoordError(f"Ký tự cột không hợp lệ: {col_char!r} trong {coord}")
    try:
        row_num = int(coord[1:])
    except ValueError:
        raise InvalidCoordError(f"Chỉ số hàng không phải số: {coord[1:]!r} trong {coord}")
    col_idx = ord(col_char) - ord('A')
    row_idx = row_num - 1
    return col_idx, row_idx


def format_coord(col_idx: int, row_idx: int) -> Coord:
    """Đổi cặp chỉ số (col_idx, row_idx) 0-indexed thành chuỗi Coord.

    Args:
        col_idx: Chỉ số cột (0 -> 'A', 1 -> 'B', ...).
        row_idx: Chỉ số hàng (0 -> '1', 1 -> '2', ...).

    Returns:
        Coord: Chuỗi định dạng như 'A1', 'C2'.
    """
    if col_idx < 0 or col_idx >= 26 or row_idx < 0:
        raise InvalidCoordError(f"Chỉ số ngoài phạm vi: col={col_idx}, row={row_idx}")
    col_char = chr(ord('A') + col_idx)
    return f"{col_char}{row_idx + 1}"


def validate_coord(coord: Coord, size: int) -> bool:
    """Kiểm tra một tọa độ có nằm gọn trong lưới kích thước N x N hay không.

    Args:
        coord: Chuỗi tọa độ cần kiểm tra.
        size: Kích thước lưới N.

    Returns:
        bool: True nếu tọa độ hợp lệ và nằm trong [0, size-1] x [0, size-1].
    """
    try:
        col_idx, row_idx = parse_coord(coord)
        return 0 <= col_idx < size and 0 <= row_idx < size
    except InvalidCoordError:
        return False


def all_coords(size: int) -> tuple[Coord, ...]:
    """Sinh danh sách tất cả các tọa độ trong lưới theo thứ tự row-major.

    Args:
        size: Kích thước lưới N.

    Returns:
        tuple[Coord, ...]: Tuple gồm N*N tọa độ, ví dụ N=3: ('A1', 'B1', 'C1', 'A2', 'B2', 'C2', 'A3', 'B3', 'C3').
    """
    return tuple(format_coord(c, r) for r in range(size) for c in range(size))


def coord_to_row_major_index(coord: Coord, size: int) -> int:
    """Chuyển tọa độ thành chỉ số phẳng 1-indexed theo thứ tự row-major (cho SAT var ID).

    Công thức: var_id = row_idx * size + col_idx + 1.

    Args:
        coord: Chuỗi tọa độ 'A1'..'C3'.
        size: Kích thước lưới N.

    Returns:
        int: Số nguyên từ 1 đến N*N.
    """
    col_idx, row_idx = parse_coord(coord)
    if not (0 <= col_idx < size and 0 <= row_idx < size):
        raise InvalidCoordError(f"Tọa độ {coord} nằm ngoài lưới {size}x{size}")
    return row_idx * size + col_idx + 1


def index_to_coord(idx: int, size: int) -> Coord:
    """Chuyển chỉ số phẳng 1-indexed (row-major) thành tọa độ Coord.

    Args:
        idx: Số nguyên từ 1 đến N*N.
        size: Kích thước lưới N.

    Returns:
        Coord: Tọa độ tương ứng trong lưới.
    """
    if idx < 1 or idx > size * size:
        raise InvalidCoordError(f"Chỉ số {idx} ngoài phạm vi 1..{size*size}")
    zero_idx = idx - 1
    row_idx = zero_idx // size
    col_idx = zero_idx % size
    return format_coord(col_idx, row_idx)
