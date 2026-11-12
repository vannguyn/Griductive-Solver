"""Thin facade coordinating GameEngine, LogicAgent, and PyQt6 GUI.

Tác dụng:
    Lớp điều phối duy nhất (Facade pattern) đứng giữa GUI và hệ thống logic bên dưới:
    - Quản lý phiên chơi hiện tại (GameSession).
    - Cung cấp giao diện gọi hàm thống nhất cho GUI:
        + load_puzzle(path): Đọc file, nạp engine, trả về PublicState ban đầu (KB_0).
        + restart(): Đưa bàn chơi về lại KB_0.
        + submit_verdict(cell, status): Nộp phán quyết và nhận VerdictOutcome.
        + hint(): Lấy gợi ý nước đi forced đầu tiên.
        + auto_solve_steps(timeout_ms): Tạo generator các bước AutoSolveStep cho QTimer/QThread.
    - Đảm bảo GUI không bao giờ phải import engine, sat hay reasoning.

Input:
    Đường dẫn puzzle, hành động của người dùng từ GUI (click ô, bấm nút).

Output:
    PublicState, VerdictOutcome, Hint, hoặc Iterator[AutoSolveStep].
    Được gọi trực tiếp bởi MainWindow trong gui/app.py.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

import time
from collections.abc import Iterator
from pathlib import Path
from griductive.agent.hint import Hint, suggest_hint
from griductive.agent.logic_agent import AutoSolveStep, LogicAgent
from griductive.domain.errors import InvalidPuzzleError
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState, VerdictOutcome
from griductive.domain.types import Status
from griductive.engine.game_engine import GameEngine
from griductive.engine.loader import load_puzzle_file
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.dpll import DPLLSolver


class GameSession:
    """Phiên làm việc quản lý trò chơi và điều phối tác tử."""

    def __init__(self) -> None:
        self._engine: GameEngine | None = None
        self._agent: LogicAgent | None = None

    @property
    def has_active_game(self) -> bool:
        """Kiểm tra xem đã nạp puzzle hay chưa."""
        return self._engine is not None

    def load_puzzle(self, path: str | Path) -> PublicState:
        """Nạp một puzzle mới từ file JSON và khởi tạo trạng thái KB_0."""
        puzzle = load_puzzle_file(path)
        solver = DPLLSolver()
        self._engine = GameEngine(puzzle, solver=solver)
        self._agent = LogicAgent(solver=solver)
        return self._engine.public_state()

    def restart(self) -> PublicState:
        """Khôi phục lại ván chơi hiện tại về trạng thái khởi đầu."""
        if not self._engine:
            raise InvalidPuzzleError("Chưa có ván chơi nào được nạp.")
        return self._engine.restart()

    def submit_verdict(self, cell: Coord, status: Status) -> VerdictOutcome:
        """Nộp kết luận thủ công từ người chơi."""
        if not self._engine:
            raise InvalidPuzzleError("Chưa có ván chơi nào được nạp.")
        return self._engine.submit_verdict(cell, status)

    def hint(self) -> Hint | None:
        """Yêu cầu một gợi ý logic an toàn dựa trên tri thức hiện có."""
        if not self._engine or not self._agent:
            return None
        pk = PublicKnowledge.from_public_state(self._engine.public_state())
        return suggest_hint(pk, self._agent.solver)

    def auto_solve_steps(self, timeout_ms: int | None = None) -> Iterator[AutoSolveStep]:
        """Tạo generator các bước giải tự động."""
        if not self._engine or not self._agent:
            raise InvalidPuzzleError("Chưa có ván chơi nào được nạp.")

        deadline = (time.perf_counter() + timeout_ms / 1000.0) if timeout_ms else None
        return self._agent.iter_steps(self._engine, deadline=deadline)
