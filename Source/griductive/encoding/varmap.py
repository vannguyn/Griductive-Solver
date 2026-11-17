"""Variable mapping between board coordinates and SAT integer literals.

Tác dụng:
    Quản lý bản đồ biến SAT:
    - Ánh xạ 2 chiều cố định theo thứ tự row-major giữa tọa độ ô Coord ("A1".."E5")
      và ID biến nguyên chính (1..N*N).
    - Cấp phát biến phụ (auxiliary variables) độc lập bắt đầu từ N*N + 1,
      đảm bảo không bao giờ trùng lặp hay làm sai lệch biến chính.

Input:
    Kích thước lưới N (size).

Output:
    Các phương thức ánh xạ: coord_to_var, var_to_coord, allocate_aux_var, allocate_aux_vars.
    Được Encoder, cardinality, clue_encoders, kb_builder sử dụng.

Người phụ trách: Nhật Tân (CNF Encoding & Clue Parsing/Validation).
"""

from griductive.domain.grid import Coord, coord_to_row_major_index, index_to_coord


class VarMap:
    """Quản lý cấp phát biến SAT số nguyên."""

    def __init__(self, size: int) -> None:
        self.size = size
        self.num_primary_vars = size * size
        self._next_aux_var = self.num_primary_vars + 1

    def coord_to_var(self, coord: Coord) -> int:
        """Chuyển tọa độ ô thành ID biến chính 1..N*N (theo row-major)."""
        return coord_to_row_major_index(coord, self.size)

    def var_to_coord(self, var_id: int) -> Coord:
        """Chuyển ID biến chính thành chuỗi tọa độ Coord."""
        return index_to_coord(var_id, self.size)

    def is_primary_var(self, var_id: int) -> bool:
        """Kiểm tra một biến có phải là biến chính đại diện cho nhân vật hay không."""
        return 1 <= abs(var_id) <= self.num_primary_vars

    def allocate_aux_var(self) -> int:
        """Cấp phát 1 biến phụ mới (bắt đầu từ N*N + 1 trở đi)."""
        var_id = self._next_aux_var
        self._next_aux_var += 1
        return var_id

    def allocate_aux_vars(self, count: int) -> tuple[int, ...]:
        """Cấp phát đồng thời count biến phụ mới."""
        return tuple(self.allocate_aux_var() for _ in range(count))

    @property
    def num_aux_vars(self) -> int:
        """Số lượng biến phụ đã được cấp phát."""
        return self._next_aux_var - (self.num_primary_vars + 1)

    @property
    def total_vars(self) -> int:
        """Tổng số biến hiện tại (biến chính + biến phụ)."""
        return self._next_aux_var - 1
