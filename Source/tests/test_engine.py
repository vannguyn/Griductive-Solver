"""Kiểm thử GameEngine: KB_0, reveal protocol và bốn kết quả verdict.

Tác dụng:
    Kiểm tra engine/game_engine.py trên puzzle 3x3 `puzzles/json_example.json`
    với bộ giải stub (không phụ thuộc DPLL). Không cần PyQt6.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from pathlib import Path
import pytest
from griductive.domain.errors import InvalidCoordError
from griductive.domain.grid import all_coords
from griductive.domain.types import SolveStatus, Status, VerdictResult
from griductive.engine.game_engine import GameEngine
from griductive.engine.loader import load_puzzle_file
from sat_stub import StubSolver

PUZZLE_PATH = Path(__file__).resolve().parent.parent / "puzzles" / "json_example.json"


@pytest.fixture
def engine() -> GameEngine:
    """Engine mới ở trạng thái KB_0."""
    return GameEngine(load_puzzle_file(PUZZLE_PATH), solver=StubSolver())


def test_initial_state_is_kb0(engine: GameEngine) -> None:
    """Ô initially_revealed đã lật; số clue công khai bằng số ô đã lật."""
    state = engine.public_state()
    revealed = [c for c in state.cells if c.revealed]
    assert [c.coord for c in revealed] == list(engine.puzzle.initially_revealed)
    assert revealed[0].status == Status.CRIMINAL  # A1
    assert len(state.revealed_clues) == len(revealed)
    assert state.solve_status == SolveStatus.RUNNING


def test_public_state_hides_solution(engine: GameEngine) -> None:
    """Ô úp không lộ status và PublicState không có thuộc tính solution."""
    state = engine.public_state()
    for cell in state.cells:
        if not cell.revealed:
            assert cell.status is None
    assert not hasattr(state, "solution")
    assert all(not hasattr(c, "solution") for c in state.cells)


def test_revealed_clues_are_row_major(engine: GameEngine) -> None:
    """Thứ tự revealed_clues ổn định theo row-major, bất kể thứ tự lật."""
    for cell in ("C1", "B1"):  # cố tình lật ngược thứ tự row-major
        engine.submit_verdict(cell, Status.INNOCENT)
    owners = [c.owner for c in engine.public_state().revealed_clues]
    order = list(all_coords(3))
    assert owners == sorted(owners, key=order.index)
    assert owners == ["A1", "B1", "C1"]


def test_forced_correct_verdict_is_accepted(engine: GameEngine) -> None:
    """Ô bị ép buộc + status đúng -> ACCEPTED, lật thẻ, mở clue."""
    outcome = engine.submit_verdict("B1", Status.INNOCENT)
    assert outcome.result == VerdictResult.ACCEPTED
    assert outcome.revealed_clue is not None
    assert outcome.revealed_clue.owner == "B1"
    cell = outcome.public_state.cell_at("B1")
    assert cell is not None and cell.revealed and cell.status == Status.INNOCENT


def test_forced_wrong_verdict_is_contradicted(engine: GameEngine) -> None:
    """Status ngược với điều bị ép buộc -> CONTRADICTED, không lật, không lộ clue."""
    before = engine.public_state()
    outcome = engine.submit_verdict("B1", Status.CRIMINAL)
    assert outcome.result == VerdictResult.CONTRADICTED
    assert outcome.revealed_clue is None
    assert outcome.public_state == before
    assert engine.public_state() == before


def test_unprovable_verdict_is_not_provable(engine: GameEngine) -> None:
    """Chưa đủ dữ kiện -> NOT_PROVABLE (kể cả khi đoán trúng), trạng thái giữ nguyên."""
    before = engine.public_state()
    for guess in (Status.CRIMINAL, Status.INNOCENT):  # B2 thật sự là Criminal
        outcome = engine.submit_verdict("B2", guess)
        assert outcome.result == VerdictResult.NOT_PROVABLE
        assert outcome.revealed_clue is None
    assert engine.public_state() == before


def test_already_revealed(engine: GameEngine) -> None:
    """Gọi lại ô đã lật -> ALREADY_REVEALED."""
    outcome = engine.submit_verdict("A1", Status.CRIMINAL)
    assert outcome.result == VerdictResult.ALREADY_REVEALED
    assert outcome.revealed_clue is None


@pytest.mark.parametrize("bad", ["Z9", "D1", "A4", "", "11"])
def test_invalid_coord_raises(engine: GameEngine, bad: str) -> None:
    """Tọa độ ngoài lưới/sai định dạng -> InvalidCoordError."""
    with pytest.raises(InvalidCoordError):
        engine.submit_verdict(bad, Status.CRIMINAL)


def test_restart_restores_kb0(engine: GameEngine) -> None:
    """restart() đưa public_state về đúng KB_0, kể cả sau khi lật vài ô."""
    kb0 = engine.public_state()
    engine.submit_verdict("B1", Status.INNOCENT)
    engine.submit_verdict("C1", Status.INNOCENT)
    assert engine.public_state() != kb0
    assert engine.restart() == kb0
    assert engine.public_state() == kb0


def test_full_playthrough_reaches_solved(engine: GameEngine) -> None:
    """Chơi theo lời giải ẩn bằng các nước ép buộc -> SOLVED."""
    solution = engine.puzzle.solution
    progressed = True
    while progressed:
        progressed = False
        for cell in all_coords(3):
            if cell in {c.coord for c in engine.public_state().cells if c.revealed}:
                continue
            status = Status.CRIMINAL if solution[cell] else Status.INNOCENT
            if engine.submit_verdict(cell, status).result == VerdictResult.ACCEPTED:
                progressed = True
    assert engine.public_state().solve_status == SolveStatus.SOLVED
