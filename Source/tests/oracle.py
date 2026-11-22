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


def test_oracle_matches_ground_truth() -> None:
    """Kiểm tra Oracle trên lưới 2x2 với các Fact và Same clue."""
    from griductive.clues.core import FactClue, SameClue
    from griductive.domain.types import Status

    # A1 là CRIMINAL, A1 và B1 cùng trạng thái
    clues = [
        FactClue("c1", "A1", "A1", Status.CRIMINAL),
        SameClue("c2", "A1", "A1", "B1"),
    ]
    oracle = BruteForceOracle(size=2, clues=clues)
    solutions = oracle.find_all_solutions()
    # 2x2 = 4 cells (A1, B1, A2, B2). A1=True, B1=True, A2 & B2 can be False/True -> 4 solutions
    assert len(solutions) == 4
    for sol in solutions:
        assert sol["A1"] is True
        assert sol["B1"] is True


def test_oracle_cross_check_3x3_puzzles() -> None:
    """Đối chiếu chéo nghiệm của BruteForceOracle với toàn bộ puzzle 3x3."""
    from pathlib import Path
    from griductive.engine.loader import load_puzzle_file
    from griductive.clues.core import FactClue
    from griductive.domain.types import Status

    puzzles_dir = Path(__file__).resolve().parent.parent / "puzzles" / "3x3"
    puzzles = sorted(puzzles_dir.glob("*.json"))
    assert len(puzzles) >= 3
    for p_path in puzzles:
        p = load_puzzle_file(p_path)
        init_clues = [
            FactClue(f"init-{c}", c, c, Status.CRIMINAL if p.solution[c] else Status.INNOCENT)
            for c in p.initially_revealed
        ]
        all_clues = list(p.clues.values()) + init_clues
        oracle = BruteForceOracle(p.size, all_clues)
        sols = oracle.find_all_solutions()
        assert len(sols) == 1, f"{p_path.name}: Oracle tìm thấy {len(sols)} nghiệm"
        assert sols[0] == p.solution, f"{p_path.name}: Nghiệm Oracle khác solution của puzzle"

