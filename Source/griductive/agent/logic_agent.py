"""Autonomous Logic Agent implementing deductive reasoning loop.

Tác dụng:
    Bộ tác tử suy diễn tự động (Auto-Solve):
    - Hoạt động thuần túy trên PublicKnowledge, chỉ tương tác với môi trường qua PublicGame Protocol.
    - Thực thi vòng lặp suy luận theo từng Wave:
        1. Dựng KB CNF từ clue đã mở và verdict đã chấp nhận.
        2. Kiểm tra tính nhất quán KB (SAT). Nếu UNSAT -> dừng (INCONSISTENT).
        3. Duyệt các ô chưa mở theo row-major, gọi classify() với 2 truy vấn entailment.
        4. Nếu tìm thấy ô bị ép (CRIMINAL hoặc INNOCENT): Nộp verdict qua game.submit_verdict().
        5. Nếu tất cả đều UNKNOWN: Dừng với trạng thái STUCK (không đoán mò).
        6. Nếu hết thời gian: Dừng với trạng thái TIMEOUT (giữ nguyên số liệu, không xóa).
    - Cung cấp:
        + iter_steps: generator yield từng AutoSolveStep cho GUI / QTimer cập nhật real-time.
        + run: thực thi toàn bộ và trả về SolveTrace hoàn chỉnh.

Input:
    game: PublicGame, deadline: float | None.

Output:
    Iterator[AutoSolveStep] hoặc SolveTrace.
    Được gọi bởi GameSession (app/session.py) và runner.py (experiments).

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import time
from collections.abc import Iterator
from dataclasses import dataclass
from griductive.agent.ports import PublicGame
from griductive.agent.trace import SolveTrace, TraceSatQuery, TraceStep
from griductive.domain.grid import all_coords
from griductive.domain.public_state import PublicState
from griductive.domain.types import Classification, SolveStatus, Status, VerdictResult
from griductive.reasoning.entailment import check_kb_consistent, classify
from griductive.reasoning.kb_builder import build_kb_cnf
from griductive.reasoning.knowledge import PublicKnowledge
from griductive.sat.cnf import SatStatus
from griductive.sat.solver import CountingSolver, SatSolver


@dataclass(frozen=True)
class AutoSolveStep:
    """Một bước tiến triển trong quá trình giải tự động, yield ra cho UI cập nhật."""
    step: TraceStep | None
    public_state: PublicState
    trace: SolveTrace


class LogicAgent:
    """Tác tử giải suy diễn tự động tuân thủ Rule 1 & Rule 2."""

    def __init__(self, solver: SatSolver) -> None:
        if isinstance(solver, CountingSolver):
            self.solver = solver
        else:
            self.solver = CountingSolver(solver)

    def iter_steps(
        self,
        game: PublicGame,
        deadline: float | None = None,
    ) -> Iterator[AutoSolveStep]:
        """Tạo generator duyệt từng bước suy diễn và nộp phán quyết."""
        start_time = time.perf_counter()
        initial_state = game.public_state()
        trace = SolveTrace(puzzle_id=initial_state.puzzle_id, solve_status=SolveStatus.RUNNING)

        step_counter = 0
        wave_counter = 0

        while True:
            current_state = game.public_state()
            if current_state.is_all_revealed():
                trace.solve_status = SolveStatus.SOLVED
                break

            wave_counter += 1
            pk = PublicKnowledge.from_public_state(current_state)
            cnf_kb, varmap, _ = build_kb_cnf(pk)

            # 1. Kiểm tra tính nhất quán KB
            kb_status = check_kb_consistent(cnf_kb, self.solver, deadline)
            if kb_status == SatStatus.UNSAT:
                trace.solve_status = SolveStatus.INCONSISTENT
                break
            if kb_status == SatStatus.TIMEOUT:
                trace.solve_status = SolveStatus.TIMEOUT
                break

            # 2. Quét tìm ô forced theo thứ tự row-major
            forced_cell = None
            forced_status = None
            forced_outcome = None
            step_start = time.perf_counter()

            for coord in all_coords(pk.size):
                if coord in pk.proved_verdicts:
                    continue  # Đã mở

                var_id = varmap.coord_to_var(coord)
                outcome = classify(cnf_kb, var_id, self.solver, deadline)

                if outcome.classification == Classification.TIMEOUT:
                    trace.solve_status = SolveStatus.TIMEOUT
                    break
                elif outcome.classification in (Classification.CRIMINAL, Classification.INNOCENT):
                    forced_cell = coord
                    forced_status = Status(outcome.classification.value)
                    forced_outcome = outcome
                    break

            if trace.solve_status == SolveStatus.TIMEOUT:
                break

            # 3. Nếu không có ô nào forced -> STUCK (không đoán mò)
            if forced_cell is None or forced_status is None or forced_outcome is None:
                trace.solve_status = SolveStatus.STUCK
                break

            # 4. Nộp verdict cho Game
            step_counter += 1
            outcome = game.submit_verdict(forced_cell, forced_status)
            step_runtime_ms = (time.perf_counter() - step_start) * 1000.0

            # Ghi nhận queries cho TraceStep
            trace_queries = tuple(
                TraceSatQuery(
                    coord=forced_cell,
                    assumed_status=Status.CRIMINAL if q.assumed_literal > 0 else Status.INNOCENT,
                    status=q.status,
                )
                for q in forced_outcome.queries
            )

            active_ids = tuple(c.id for c in pk.revealed_clues)
            trace_step = TraceStep(
                step=step_counter,
                wave=wave_counter,
                cell=forced_cell,
                classification=forced_outcome.classification,
                active_clue_ids=active_ids,
                sat_queries=trace_queries,
                verdict_result=outcome.result,
                revealed_clue_id=outcome.revealed_clue.id if outcome.revealed_clue else None,
                runtime_ms=step_runtime_ms,
            )
            trace.steps.append(trace_step)

            # Cập nhật số liệu tích lũy
            trace.total_sat_calls = self.solver.calls
            trace.total_decisions = self.solver.total_decisions
            trace.total_propagations = self.solver.total_propagations
            trace.total_backtracks = self.solver.total_backtracks
            trace.reveal_waves = wave_counter
            trace.total_runtime_ms = (time.perf_counter() - start_time) * 1000.0

            yield AutoSolveStep(step=trace_step, public_state=outcome.public_state, trace=trace)

            if outcome.result != VerdictResult.ACCEPTED:
                # Nếu bị từ chối ngoài dự kiến -> dừng
                trace.solve_status = SolveStatus.STUCK
                break

        trace.total_runtime_ms = (time.perf_counter() - start_time) * 1000.0
        yield AutoSolveStep(step=None, public_state=game.public_state(), trace=trace)

    def run(
        self,
        game: PublicGame,
        deadline: float | None = None,
    ) -> SolveTrace:
        """Chạy toàn bộ quá trình tự động giải cho đến khi kết thúc và trả về SolveTrace."""
        last_step = None
        for step in self.iter_steps(game, deadline=deadline):
            last_step = step
        if last_step:
            return last_step.trace
        return SolveTrace(puzzle_id="unknown", solve_status=SolveStatus.STUCK)
