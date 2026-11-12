"""Ground truth brute-force oracle for small puzzle verification.

Tác dụng:
    Bộ kiểm chứng chân lý (Ground Truth Oracle) bằng thuật toán vét cạn:
    - Với lưới nhỏ (N <= 4, tức 2^(N^2) phép gán), duyệt qua toàn bộ các khả năng gán
      chân trị của các ô và kiểm tra trực tiếp qua hàm clue.evaluate().
    - Hoàn toàn không dùng CNF hay DPLL solver.
    - Cung cấp chân lý tuyệt đối để kiểm tra tính đúng đắn của DPLL và Entailment.

Input:
    Danh sách các Clue và kích thước lưới size N.

Output:
    Danh sách tất cả các phép gán (models: list[dict[Coord, bool]]) thỏa mãn mọi clue.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import itertools
from collections.abc import Sequence
from griductive.clues.base import Clue
from griductive.domain.grid import Coord, all_coords


class BruteForceOracle:
    """Bộ giải vét cạn độc lập dựa trên ngữ nghĩa của Clue."""

    def __init__(self, size: int, clues: Sequence[Clue]) -> None:
        self.size = size
        self.clues = clues
        self.coords = all_coords(size)

    def find_all_solutions(self) -> list[dict[Coord, bool]]:
        """Duyệt toàn bộ 2^(N^2) phép gán để tìm tất cả các nghiệm thỏa mãn."""
        if self.size > 4:
            raise ValueError("BruteForceOracle chỉ hỗ trợ lưới N <= 4 do bùng nổ tổ hợp 2^(N^2).")

        solutions: list[dict[Coord, bool]] = []
        n_cells = len(self.coords)

        for bits in itertools.product([False, True], repeat=n_cells):
            assignment = {self.coords[i]: bits[i] for i in range(n_cells)}
            if all(clue.evaluate(assignment) for clue in self.clues):
                solutions.append(assignment)

        return solutions

    def is_unique(self) -> bool:
        """Kiểm tra xem tập nghiệm có đúng duy nhất 1 nghiệm hay không."""
        return len(self.find_all_solutions()) == 1
