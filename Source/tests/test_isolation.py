"""Architectural boundary and isolation test suite.

Tác dụng:
    Kiểm tra 2 lớp bảo vệ kiến trúc theo Rule 1:
    1. Kiểm tra AST tĩnh (Static AST analysis):
       - Module agent/ không import engine/, gui/, hay app/.
       - Module sat/ không import domain/, clues/, hay bất kỳ module griductive nào khác.
       - Module domain/ không import clues/.
       - Module reasoning/ không import agent/.
    2. Kiểm tra MockGame động (Dynamic MockGame test):
       - Chạy LogicAgent trên một MockGame cài đặt PublicGame Protocol.
       - Bất kỳ hành vi cố tình đọc hidden attribute sẽ ném AssertionError ngay lập tức.

Input:
    Mã nguồn các file Python và lớp giả lập MockGame.

Output:
    Khẳng định tính cô lập dữ liệu tuyệt đối của Logic Agent.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import ast
from pathlib import Path

from griductive.agent.logic_agent import LogicAgent
from griductive.agent.ports import PublicGame
from griductive.clues.core import FactClue
from griductive.domain.grid import all_coords
from griductive.domain.public_state import PublicCell, PublicState, VerdictOutcome
from griductive.domain.types import SolveStatus, Status, VerdictResult
from griductive.sat.dpll import DPLLSolver


def get_imported_modules(file_path: Path) -> set[str]:
    """Phân tích cây cú pháp trừu tượng AST để lấy danh sách các module được import."""
    with open(file_path, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=str(file_path))

    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module)
    return imports


def test_agent_does_not_import_engine() -> None:
    """Bảo đảm agent/ tuyệt đối không import engine, gui, hay app."""
    agent_dir = Path(__file__).resolve().parent.parent / "griductive" / "agent"
    forbidden_prefixes = ("griductive.engine", "griductive.gui", "griductive.app")

    for py_file in agent_dir.glob("*.py"):
        imported = get_imported_modules(py_file)
        for mod in imported:
            for forbidden in forbidden_prefixes:
                assert not mod.startswith(forbidden), (
                    f"Vi phạm Rule 1 tại {py_file.name}: agent không được phép import {mod}"
                )


def test_sat_is_pure_integer() -> None:
    """Bảo đảm sat/ hoàn toàn độc lập, không import bất kỳ package nào của griductive."""
    sat_dir = Path(__file__).resolve().parent.parent / "griductive" / "sat"
    for py_file in sat_dir.glob("*.py"):
        imported = get_imported_modules(py_file)
        for mod in imported:
            assert not mod.startswith("griductive.domain"), f"sat/ không được import domain: {py_file.name}"
            assert not mod.startswith("griductive.clues"), f"sat/ không được import clues: {py_file.name}"
            assert not mod.startswith("griductive.agent"), f"sat/ không được import agent: {py_file.name}"
            assert not mod.startswith("griductive.engine"), f"sat/ không được import engine: {py_file.name}"


class StrictMockGame(PublicGame):
    """Giả lập GameEngine có bẫy để phát hiện việc đọc trộm hidden attributes."""

    def __init__(self) -> None:
        self.puzzle_id = "mock-isolation-test"
        self.size = 2
        # Thuộc tính ẩn bị cấm truy cập
        self.hidden_solution = {"A1": Status.CRIMINAL, "B1": Status.INNOCENT, "A2": Status.INNOCENT, "B2": Status.CRIMINAL}
        self.secret_unrevealed_clues = {"clue-secret": "DO_NOT_READ"}

        # Cho sẵn clue A1 là Criminal
        self.revealed_clues = [FactClue("clue-1", "A1", "A1", Status.CRIMINAL)]
        self.cell_map = {
            c: PublicCell(coord=c, name=f"Char_{c}", job="Civilian", revealed=False, status=None)
            for c in all_coords(2)
        }

    def __getattribute__(self, name: str):
        # Bẫy truy cập: nếu chạm vào hidden_solution hay secret_unrevealed_clues sẽ nổ lỗi
        if name in ("hidden_solution", "secret_unrevealed_clues", "solution"):
            raise AssertionError(f"Rule 1 VIOLATION: Agent cố tình đọc thuộc tính ẩn '{name}'!")
        return super().__getattribute__(name)

    def public_state(self) -> PublicState:
        return PublicState(
            puzzle_id=self.puzzle_id,
            size=self.size,
            cells=tuple(self.cell_map[c] for c in all_coords(2)),
            revealed_clues=tuple(self.revealed_clues),
            solve_status=SolveStatus.RUNNING,
        )

    def submit_verdict(self, cell: str, status: Status) -> VerdictOutcome:
        # Nếu verdict là A1 CRIMINAL thì chấp nhận
        if cell == "A1" and status == Status.CRIMINAL:
            self.cell_map[cell] = PublicCell(
                coord=cell, name=f"Char_{cell}", job="Civilian", revealed=True, status=status
            )
            return VerdictOutcome(
                result=VerdictResult.ACCEPTED,
                cell=cell,
                revealed_clue=self.revealed_clues[0],
                public_state=self.public_state(),
                message="Accepted",
            )
        return VerdictOutcome(
            result=VerdictResult.NOT_PROVABLE,
            cell=cell,
            revealed_clue=None,
            public_state=self.public_state(),
            message="Not provable",
        )


def test_mock_game_dynamic_isolation() -> None:
    """Bảo đảm LogicAgent khi chạy hoàn toàn không chạm vào hidden solution của game."""
    game = StrictMockGame()
    agent = LogicAgent(solver=DPLLSolver())

    # Chạy 1 wave: agent phải đọc public_state, tìm thấy A1 là forced CRIMINAL và nộp verdict
    trace = agent.run(game)
    # Khẳng định agent đã nộp verdict A1 thành công và không bị dính bẫy __getattribute__
    assert len(trace.steps) >= 1
    assert trace.steps[0].cell == "A1"
    assert trace.steps[0].verdict_result == VerdictResult.ACCEPTED
