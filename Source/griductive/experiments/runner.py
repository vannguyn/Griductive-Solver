import json
import time
from pathlib import Path
from griductive.agent.logic_agent import LogicAgent
from griductive.encoding.encoder import Encoder
from griductive.encoding.varmap import VarMap
from griductive.engine.game_engine import GameEngine
from griductive.engine.loader import load_puzzle_from_dict
from griductive.experiments.metrics import PuzzleMetrics
from griductive.sat.dpll import DPLLSolver


def run_benchmark_on_puzzle(
    file_path: Path,
    timeout_seconds: float = 30.0,
) -> PuzzleMetrics:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    allow_inconsistent = bool(raw_data.get("allow_inconsistent", False))
    effective_timeout = float(raw_data.get("benchmark_timeout_seconds", timeout_seconds))
    puzzle = load_puzzle_from_dict(raw_data, verify_solution=not allow_inconsistent)

    t0 = time.perf_counter()
    varmap = VarMap(puzzle.size)
    encoder = Encoder(varmap=varmap)
    cnf, enc_stats = encoder.encode(list(puzzle.clues.values()))
    encode_ms = (time.perf_counter() - t0) * 1000.0

    engine = GameEngine(puzzle)
    agent = LogicAgent(solver=DPLLSolver())
    deadline = time.perf_counter() + effective_timeout

    t1 = time.perf_counter()
    trace = agent.run(engine, deadline=deadline)
    solve_ms = (time.perf_counter() - t1) * 1000.0

    return PuzzleMetrics(
        puzzle_id=puzzle.id,
        grid_size=puzzle.size,
        primary_vars=enc_stats.primary_vars,
        aux_vars=enc_stats.aux_vars,
        clauses=enc_stats.clauses,
        total_sat_calls=trace.total_sat_calls,
        total_decisions=trace.total_decisions,
        total_propagations=trace.total_propagations,
        total_backtracks=trace.total_backtracks,
        reasoning_steps=len(trace.steps),
        reveal_waves=trace.reveal_waves,
        encode_time_ms=encode_ms,
        solve_time_ms=solve_ms,
        total_runtime_ms=encode_ms + solve_ms,
        outcome=trace.solve_status,
    )


def run_all_benchmarks(
    puzzles_dir: str | Path,
    timeout_seconds: float = 30.0,
) -> list[PuzzleMetrics]:
    p_path = Path(puzzles_dir)
    json_files = sorted(p_path.glob("**/*.json"))
    results: list[PuzzleMetrics] = []

    for f in json_files:
        try:
            m = run_benchmark_on_puzzle(f, timeout_seconds=timeout_seconds)
            results.append(m)
        except Exception as e:
            print(f"Lỗi khi chạy benchmark {f.name}: {e}")

    return results