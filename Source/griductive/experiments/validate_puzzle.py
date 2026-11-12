"""Offline puzzle validator verifying uniqueness and solvable-without-guessing property.

Tác dụng:
    Công cụ dòng lệnh (CLI offline) kiểm tra tính chuẩn tắc của file puzzle JSON:
    1. Kiểm tra schema, kích thước N in {3, 4, 5}, ánh xạ 1-1 owner và characters.
    2. Kiểm tra tính chân thực của solution ẩn: clue.evaluate(solution) == True với mọi clue.
    3. Kiểm tra tính duy nhất: check_uniqueness == UniquenessResult.UNIQUE trên biến chính.
    4. Kiểm tra tính giải được không cần đoán mò: LogicAgent giải thành công (SOLVED).
    Giúp lọc các puzzle không đạt chuẩn trước khi đưa vào thư mục Source/puzzles/.

Input:
    Đường dẫn tới file JSON puzzle (path: str | Path).

Output:
    tuple[bool, str]: (is_valid, log_message).

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

from pathlib import Path
from griductive.agent.logic_agent import LogicAgent
from griductive.domain.errors import InvalidPuzzleError
from griductive.domain.types import SolveStatus, UniquenessResult
from griductive.encoding.encoder import Encoder
from griductive.encoding.varmap import VarMap
from griductive.engine.game_engine import GameEngine
from griductive.engine.loader import load_puzzle_file
from griductive.reasoning.uniqueness import check_uniqueness
from griductive.sat.dpll import DPLLSolver


def validate_puzzle_file(path: str | Path, direct_threshold: int = 64) -> tuple[bool, str]:
    """Kiểm tra toàn diện tính hợp lệ của puzzle."""
    try:
        puzzle = load_puzzle_file(path)
    except Exception as e:
        return False, f"Lỗi load puzzle: {e}"

    # 1. Kiểm tra uniqueness qua SAT
    varmap = VarMap(puzzle.size)
    encoder = Encoder(varmap=varmap, direct_threshold=direct_threshold)
    cnf, _ = encoder.encode(list(puzzle.clues.values()))

    solver = DPLLSolver()
    uniq_res = check_uniqueness(cnf, num_primary_vars=varmap.num_primary_vars, solver=solver)
    if uniq_res.result != UniquenessResult.UNIQUE:
        return False, f"Kiểm tra Uniqueness thất bại: kết quả là {uniq_res.result}"

    # 2. Kiểm tra tính giải được không cần đoán qua LogicAgent
    engine = GameEngine(puzzle)
    agent = LogicAgent(solver=solver)
    trace = agent.run(engine)

    if trace.solve_status != SolveStatus.SOLVED:
        return False, f"LogicAgent không thể giải hoàn tất mà không đoán: {trace.solve_status}"

    return True, f"Puzzle hợp lệ: UNIQUE và giải thành công qua {len(trace.steps)} bước suy diễn."
