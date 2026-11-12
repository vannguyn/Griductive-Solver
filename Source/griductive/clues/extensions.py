"""Extension clue implementations and semantic evaluators.

Tác dụng:
    Định nghĩa các loại manh mối mở rộng (Extensions, bắt buộc >= 2 theo yêu cầu đồ án):
    - PARITY: Số lượng Criminal trong vùng là chẵn (EVEN) hoặc lẻ (ODD).
    - COMPOUND: Kết hợp logic giữa các manh mối con (AND, OR, NOT).
    - COMPARE_COUNT (Tùy chọn): So sánh số lượng Criminal giữa 2 vùng.

Input:
    Các tham số đặc thù của từng extension clue.

Output:
    Các đối tượng Clue mở rộng, cài đặt cells() và evaluate().
    Được parser nạp và encoder mã hóa.

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from collections.abc import Mapping
from griductive.clues.base import Clue
from griductive.domain.grid import Coord
from griductive.domain.regions import RegionSpec


class ParityClue(Clue):
    """Manh mối tính chẵn/lẻ của số Criminal trong vùng.

    parity: 'EVEN' (chẵn: 0, 2, 4...) hoặc 'ODD' (lẻ: 1, 3, 5...).
    """

    def __init__(
        self,
        id: str,
        owner: Coord,
        parity: str,
        region_spec: RegionSpec,
        region_cells: tuple[Coord, ...],
    ) -> None:
        super().__init__(id, owner, "PARITY")
        self.parity = parity.upper()
        self.region_spec = region_spec
        self.region_cells = region_cells

    def cells(self) -> tuple[Coord, ...]:
        return self.region_cells

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        cnt = sum(1 for c in self.region_cells if assign.get(c, False) is True)
        if self.parity == "EVEN":
            return cnt % 2 == 0
        elif self.parity == "ODD":
            return cnt % 2 == 1
        return False


class CompoundClue(Clue):
    """Manh mối phức hợp kết hợp các manh mối con theo phép toán AND, OR, hoặc NOT."""

    def __init__(
        self,
        id: str,
        owner: Coord,
        op: str,
        sub_clues: tuple[Clue, ...],
    ) -> None:
        super().__init__(id, owner, "COMPOUND")
        self.op = op.upper()
        self.sub_clues = sub_clues

    def cells(self) -> tuple[Coord, ...]:
        seen: set[Coord] = set()
        res: list[Coord] = []
        for sub in self.sub_clues:
            for c in sub.cells():
                if c not in seen:
                    seen.add(c)
                    res.append(c)
        return tuple(res)

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        if self.op == "AND":
            return all(sub.evaluate(assign) for sub in self.sub_clues)
        elif self.op == "OR":
            return any(sub.evaluate(assign) for sub in self.sub_clues)
        elif self.op == "NOT":
            if len(self.sub_clues) != 1:
                return False
            return not self.sub_clues[0].evaluate(assign)
        return False


class CompareCountClue(Clue):
    """(Mở rộng tùy chọn) So sánh số Criminal giữa hai vùng: left_region vs right_region.

    op: 'GREATER' (>), 'LESS' (<), 'EQUAL' (==).
    """

    def __init__(
        self,
        id: str,
        owner: Coord,
        op: str,
        region_left_cells: tuple[Coord, ...],
        region_right_cells: tuple[Coord, ...],
    ) -> None:
        super().__init__(id, owner, "COMPARE_COUNT")
        self.op = op.upper()
        self.region_left_cells = region_left_cells
        self.region_right_cells = region_right_cells

    def cells(self) -> tuple[Coord, ...]:
        seen = set(self.region_left_cells)
        return self.region_left_cells + tuple(c for c in self.region_right_cells if c not in seen)

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        cnt_left = sum(1 for c in self.region_left_cells if assign.get(c, False) is True)
        cnt_right = sum(1 for c in self.region_right_cells if assign.get(c, False) is True)
        if self.op == "GREATER":
            return cnt_left > cnt_right
        elif self.op == "LESS":
            return cnt_left < cnt_right
        elif self.op == "EQUAL":
            return cnt_left == cnt_right
        return False
