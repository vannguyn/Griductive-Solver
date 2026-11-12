"""Core clue implementations and semantic evaluators.

Tác dụng:
    Định nghĩa 6 loại manh mối cốt lõi: FACT, SAME, DIFFERENT, EXACTLY, AT_LEAST, AT_MOST.
    Mỗi class cài đặt:
    - cells() -> tuple[Coord, ...]: trả về các ô liên quan
    - evaluate(assign: Mapping[Coord, bool]) -> bool: đánh giá trực tiếp ngữ nghĩa chân lý.

Input:
    Các tham số đặc trưng của từng clue (tọa độ ô, số k, region_cells).

Output:
    Các đối tượng Clue cụ thể.
    Phương thức evaluate() phục vụ loader (xác thực puzzle) và test_encoder_vs_eval.py (so sánh chéo).

Người phụ trách: Nhật Minh (SAT, Reasoning & Clue Semantics).
"""

from collections.abc import Mapping
from griductive.clues.base import Clue
from griductive.domain.grid import Coord
from griductive.domain.regions import RegionSpec
from griductive.domain.types import Status


class FactClue(Clue):
    """Manh mối khẳng định trực tiếp trạng thái của một nhân vật.

    Ví dụ: 'Abel là Criminal' hoặc 'Mara là Innocent'.
    """

    def __init__(self, id: str, owner: Coord, target_cell: Coord, target_status: Status) -> None:
        super().__init__(id, owner, "FACT")
        self.target_cell = target_cell
        self.target_status = target_status

    def cells(self) -> tuple[Coord, ...]:
        return (self.target_cell,)

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        expected_bool = (self.target_status == Status.CRIMINAL)
        return assign.get(self.target_cell) == expected_bool


class SameClue(Clue):
    """Manh mối hai nhân vật có cùng trạng thái (cùng Criminal hoặc cùng Innocent)."""

    def __init__(self, id: str, owner: Coord, cell_a: Coord, cell_b: Coord) -> None:
        super().__init__(id, owner, "SAME")
        self.cell_a = cell_a
        self.cell_b = cell_b

    def cells(self) -> tuple[Coord, ...]:
        return (self.cell_a, self.cell_b)

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        return assign.get(self.cell_a) == assign.get(self.cell_b)


class DifferentClue(Clue):
    """Manh mối hai nhân vật có trạng thái trái ngược nhau (một Criminal, một Innocent)."""

    def __init__(self, id: str, owner: Coord, cell_a: Coord, cell_b: Coord) -> None:
        super().__init__(id, owner, "DIFFERENT")
        self.cell_a = cell_a
        self.cell_b = cell_b

    def cells(self) -> tuple[Coord, ...]:
        return (self.cell_a, self.cell_b)

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        return assign.get(self.cell_a) != assign.get(self.cell_b)


class ExactlyClue(Clue):
    """Manh mối có chính xác k Criminal trong vùng chỉ định."""

    def __init__(
        self,
        id: str,
        owner: Coord,
        k: int,
        region_spec: RegionSpec,
        region_cells: tuple[Coord, ...],
    ) -> None:
        super().__init__(id, owner, "EXACTLY")
        self.k = k
        self.region_spec = region_spec
        self.region_cells = region_cells

    def cells(self) -> tuple[Coord, ...]:
        return self.region_cells

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        criminal_count = sum(1 for c in self.region_cells if assign.get(c, False) is True)
        return criminal_count == self.k


class AtLeastClue(Clue):
    """Manh mối có ít nhất k Criminal trong vùng chỉ định."""

    def __init__(
        self,
        id: str,
        owner: Coord,
        k: int,
        region_spec: RegionSpec,
        region_cells: tuple[Coord, ...],
    ) -> None:
        super().__init__(id, owner, "AT_LEAST")
        self.k = k
        self.region_spec = region_spec
        self.region_cells = region_cells

    def cells(self) -> tuple[Coord, ...]:
        return self.region_cells

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        criminal_count = sum(1 for c in self.region_cells if assign.get(c, False) is True)
        return criminal_count >= self.k


class AtMostClue(Clue):
    """Manh mối có nhiều nhất k Criminal trong vùng chỉ định."""

    def __init__(
        self,
        id: str,
        owner: Coord,
        k: int,
        region_spec: RegionSpec,
        region_cells: tuple[Coord, ...],
    ) -> None:
        super().__init__(id, owner, "AT_MOST")
        self.k = k
        self.region_spec = region_spec
        self.region_cells = region_cells

    def cells(self) -> tuple[Coord, ...]:
        return self.region_cells

    def evaluate(self, assign: Mapping[Coord, bool]) -> bool:
        criminal_count = sum(1 for c in self.region_cells if assign.get(c, False) is True)
        return criminal_count <= self.k
