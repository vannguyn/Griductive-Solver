"""Kiểm thử loader (schema puzzle) và GameSession (facade).

Tác dụng:
    - load_puzzle_from_dict / load_puzzle_file ném InvalidPuzzleError đúng các ca sai.
    - GameSession báo lỗi khi chưa nạp puzzle, và Auto Solve giải xong puzzle ví dụ.
    DPLLSolver được thay bằng StubSolver để độc lập với phần của Minh. Không cần PyQt6.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

import copy
import json
from pathlib import Path
from typing import Any
import pytest
from griductive.app import session as session_module
from griductive.app.session import GameSession
from griductive.domain.errors import InvalidPuzzleError
from griductive.domain.types import SolveStatus, Status, VerdictResult
from griductive.engine.loader import load_puzzle_file, load_puzzle_from_dict
from sat_stub import StubSolver

PUZZLE_PATH = Path(__file__).resolve().parent.parent / "puzzles" / "json_example.json"


def valid_data() -> dict[str, Any]:
    """Bản sao mới của puzzle ví dụ dưới dạng dict."""
    with open(PUZZLE_PATH, encoding="utf-8") as f:
        return json.load(f)


def test_valid_puzzle_loads() -> None:
    """Puzzle ví dụ hợp lệ nạp được."""
    puzzle = load_puzzle_from_dict(valid_data())
    assert puzzle.size == 3 and len(puzzle.clues) == 9


def test_non_dict_rejected() -> None:
    """Dữ liệu gốc không phải dict bị từ chối."""
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict([])  # type: ignore[arg-type]


@pytest.mark.parametrize("size", [2, 6, "3", None])
def test_bad_size(size: Any) -> None:
    """size ngoài {3, 4, 5} bị từ chối."""
    data = valid_data()
    data["size"] = size
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_missing_character() -> None:
    """Thiếu nhân vật bị từ chối."""
    data = valid_data()
    data["characters"].pop()
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_character_with_bad_coord() -> None:
    """Nhân vật có tọa độ ngoài lưới bị từ chối."""
    data = valid_data()
    data["characters"][0]["cell"] = "Z9"
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_bad_initially_revealed() -> None:
    """initially_revealed chứa tọa độ sai bị từ chối."""
    data = valid_data()
    data["initially_revealed"] = ["Z9"]
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_solution_missing_cell() -> None:
    """solution thiếu ô (đủ số lượng nhưng sai khóa) bị từ chối."""
    data = valid_data()
    data["solution"]["Z9"] = data["solution"].pop("C3")
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_solution_too_short() -> None:
    """solution thiếu số ô bị từ chối."""
    data = valid_data()
    del data["solution"]["C3"]
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_solution_value_not_bool() -> None:
    """Giá trị solution không phải bool bị từ chối."""
    data = valid_data()
    data["solution"]["A1"] = 1
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_duplicate_clue_owner() -> None:
    """Hai clue cùng owner bị từ chối."""
    data = valid_data()
    data["clues"][1]["owner"] = data["clues"][0]["owner"]
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_clue_contradicts_solution() -> None:
    """Clue sai với solution ẩn bị từ chối."""
    data = copy.deepcopy(valid_data())
    data["clues"][1]["status"] = "INNOCENT"  # B1: "B2 là Innocent", nhưng B2 là Criminal
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_from_dict(data)


def test_missing_file(tmp_path: Path) -> None:
    """File không tồn tại bị từ chối."""
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_file(tmp_path / "khong_ton_tai.json")


def test_broken_json(tmp_path: Path) -> None:
    """JSON hỏng bị từ chối."""
    path = tmp_path / "hong.json"
    path.write_text("{ not json", encoding="utf-8")
    with pytest.raises(InvalidPuzzleError):
        load_puzzle_file(path)


@pytest.fixture
def session(monkeypatch: pytest.MonkeyPatch) -> GameSession:
    """GameSession dùng StubSolver thay DPLLSolver, đã nạp puzzle ví dụ."""
    monkeypatch.setattr(session_module, "DPLLSolver", StubSolver)
    s = GameSession()
    s.load_puzzle(PUZZLE_PATH)
    return s


def test_session_before_load_raises() -> None:
    """Gọi trước khi nạp puzzle: lỗi rõ ràng, hint trả None."""
    s = GameSession()
    assert not s.has_active_game
    with pytest.raises(InvalidPuzzleError):
        s.submit_verdict("A1", Status.CRIMINAL)
    with pytest.raises(InvalidPuzzleError):
        s.restart()
    with pytest.raises(InvalidPuzzleError):
        s.auto_solve_steps()
    assert s.hint() is None


def test_session_hint_is_forced_move(session: GameSession) -> None:
    """Hint là một nước ép buộc và chấp nhận được khi nộp."""
    hint = session.hint()
    assert hint is not None
    outcome = session.submit_verdict(hint.cell, hint.suggested_status)
    assert outcome.result == VerdictResult.ACCEPTED


def test_session_restart_after_moves(session: GameSession) -> None:
    """restart() trả về đúng trạng thái ngay sau load."""
    kb0 = session.restart()
    session.submit_verdict("B1", Status.INNOCENT)
    assert session.restart() == kb0


def test_auto_solve_reaches_solved(session: GameSession) -> None:
    """Auto Solve lật mọi ô, không bước nào bị từ chối, kết thúc SOLVED."""
    steps = list(session.auto_solve_steps())
    real = [s.step for s in steps if s.step is not None]
    assert real and all(st.verdict_result == VerdictResult.ACCEPTED for st in real)
    last = steps[-1]
    assert last.step is None
    assert last.trace.solve_status == SolveStatus.SOLVED
    assert last.public_state.is_all_revealed()
