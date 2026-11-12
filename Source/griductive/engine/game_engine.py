"""Game Engine managing game state, verdict verification, and clue revealing.

Tác dụng:
    Thực thi luật chơi và quản lý vòng đời ván game:
    - Nắm giữ đối tượng Puzzle (gồm cả solution ẩn và các clue chưa mở).
    - Cung cấp public_state() an toàn, tuyệt đối không tiết lộ thông tin mật.
    - Xử lý submit_verdict(cell, status):
        + Không dùng solution ẩn để chấm điểm tùy tiện!
        + Dùng module reasoning kiểm tra xem verdict có được CHỨNG MINH bởi PublicKnowledge hiện tại hay không:
            * Nếu đúng với entailment -> ACCEPTED, lật thẻ, giải phóng clue của ô này.
            * Nếu ngược với entailment -> CONTRADICTED, cảnh báo lỗi, không lật thẻ.
            * Nếu UNKNOWN hoặc TIMEOUT -> NOT_PROVABLE (chưa đủ dữ kiện, cấm đoán mò).
            * Nếu ô đã lật trước đó -> ALREADY_REVEALED.
    - Cung cấp restart() để khôi phục về trạng thái khởi tạo KB_0 (initially_revealed).
    - Thỏa mãn PublicGame Protocol mà không import module agent/.

Input:
    Đối tượng Puzzle và tùy chọn SatSolver.

Output:
    PublicState và VerdictOutcome.
    Được gọi bởi GameSession (app/session.py).

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from griductive.clues.base import Clue
from griductive.domain.errors import InvalidCoordError
from griductive.domain.grid import Coord, all_coords, validate_coord
from griductive.domain.public_state import PublicCell, PublicState, VerdictOutcome
from griductive.domain.types import Classification, SolveStatus, Status, VerdictResult
from griductive.engine.puzzle import Puzzle
from griductive.reasoning.entailment import classify
from griductive.reasoning.kb_builder import build_kb_cnf
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.dpll import DPLLSolver
from griductive.sat.solver import SatSolver


class GameEngine:
    """Bộ máy trò chơi điều phối trạng thái ván cờ."""

    def __init__(self, puzzle: Puzzle, solver: SatSolver | None = None) -> None:
        self.puzzle = puzzle
        self.solver: SatSolver = solver if solver is not None else DPLLSolver()
        self._revealed_cells: set[Coord] = set(puzzle.initially_revealed)
        self._cell_statuses: dict[Coord, Status] = {}

        # Khởi tạo trạng thái cho các ô ban đầu (KB_0)
        for c in puzzle.initially_revealed:
            is_crim = puzzle.solution[c]
            self._cell_statuses[c] = Status.CRIMINAL if is_crim else Status.INNOCENT

        self._solve_status = SolveStatus.RUNNING

    def public_state(self) -> PublicState:
        """Sinh ra PublicState hiện tại an toàn cho Agent và GUI."""
        cells: list[PublicCell] = []
        for c in all_coords(self.puzzle.size):
            char_info = self.puzzle.characters[c]
            is_rev = c in self._revealed_cells
            status = self._cell_statuses.get(c) if is_rev else None
            cells.append(PublicCell(coord=c, name=char_info.name, job=char_info.job, revealed=is_rev, status=status))

        # Lấy các clue của những ô đã được lật
        revealed_clues: list[Clue] = []
        for c in self._revealed_cells:
            if c in self.puzzle.clues:
                revealed_clues.append(self.puzzle.clues[c])

        # Kiểm tra hoàn thành
        if len(self._revealed_cells) == self.puzzle.size * self.puzzle.size:
            self._solve_status = SolveStatus.SOLVED

        return PublicState(
            puzzle_id=self.puzzle.id,
            size=self.puzzle.size,
            cells=tuple(cells),
            revealed_clues=tuple(revealed_clues),
            solve_status=self._solve_status,
        )

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Xác thực và nộp kết luận về trạng thái một ô."""
        if not validate_coord(cell, self.puzzle.size):
            raise InvalidCoordError(f"Tọa độ ô không hợp lệ: {cell}")

        if cell in self._revealed_cells:
            return VerdictOutcome(
                result=VerdictResult.ALREADY_REVEALED,
                cell=cell,
                revealed_clue=None,
                public_state=self.public_state(),
                message=f"Ô {cell} đã được lật mở từ trước.",
            )

        # Kiểm tra tính bị ép buộc bởi PublicKnowledge (Không nhìn solution!)
        pk = PublicKnowledge.from_public_state(self.public_state())
        cnf_kb, varmap, _ = build_kb_cnf(pk)
        var_id = varmap.coord_to_var(cell)
        outcome = classify(cnf_kb, var_id, self.solver)

        if outcome.classification == Classification.INCONSISTENT:
            self._solve_status = SolveStatus.INCONSISTENT
            return VerdictOutcome(
                result=VerdictResult.NOT_PROVABLE,
                cell=cell,
                revealed_clue=None,
                public_state=self.public_state(),
                message="Cơ sở tri thức hiện tại bị mâu thuẫn logic (INCONSISTENT).",
            )

        if outcome.classification in (Classification.UNKNOWN, Classification.TIMEOUT):
            return VerdictOutcome(
                result=VerdictResult.NOT_PROVABLE,
                cell=cell,
                revealed_clue=None,
                public_state=self.public_state(),
                message=f"Chưa đủ dữ kiện để khẳng định {cell} là {status.value}. Không được đoán mò!",
            )

        entailed_status = Status(outcome.classification.value)
        if entailed_status != status:
            return VerdictOutcome(
                result=VerdictResult.CONTRADICTED,
                cell=cell,
                revealed_clue=None,
                public_state=self.public_state(),
                message=f"Phán quyết sai! Logic hiện tại ép buộc ô {cell} phải là {entailed_status.value}.",
            )

        # Chấp nhận verdict
        self._revealed_cells.add(cell)
        self._cell_statuses[cell] = status
        new_clue = self.puzzle.clues.get(cell)

        return VerdictOutcome(
            result=VerdictResult.ACCEPTED,
            cell=cell,
            revealed_clue=new_clue,
            public_state=self.public_state(),
            message=f"Chính xác! Ô {cell} là {status.value}.",
        )

    def restart(self) -> PublicState:
        """Khôi phục bàn chơi về trạng thái ban đầu KB_0."""
        self._revealed_cells = set(self.puzzle.initially_revealed)
        self._cell_statuses = {}
        for c in self.puzzle.initially_revealed:
            is_crim = self.puzzle.solution[c]
            self._cell_statuses[c] = Status.CRIMINAL if is_crim else Status.INNOCENT
        self._solve_status = SolveStatus.RUNNING
        return self.public_state()
