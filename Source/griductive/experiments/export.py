"""Export utilities for experiment benchmark metrics (CSV, LaTeX, plots).

Tác dụng:
    Xuất các số liệu thực nghiệm thu thập được thành:
    - File CSV (Source/results/metrics.csv) phục vụ phân tích.
    - Bảng LaTeX (Source/results/metrics.tex) dán trực tiếp vào Final Report (30 điểm).
    - Biểu đồ thời gian chạy theo kích thước lưới (runtime_by_grid.png).

Input:
    list[PuzzleMetrics] và đường dẫn file xuất.

Output:
    Các file CSV, TEX, PNG được ghi vào đĩa.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import csv
from pathlib import Path
from griductive.experiments.metrics import PuzzleMetrics


def export_to_csv(metrics: list[PuzzleMetrics], output_path: str | Path) -> None:
    """Xuất danh sách chỉ số ra file CSV."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    with open(p, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "Puzzle ID", "Size", "Primary Vars", "Aux Vars", "Clauses",
            "SAT Calls", "Decisions", "Propagations", "Backtracks",
            "Steps", "Waves", "Encode (ms)", "Solve (ms)", "Total (ms)", "Outcome"
        ])
        for m in metrics:
            writer.writerow([
                m.puzzle_id, m.grid_size, m.primary_vars, m.aux_vars, m.clauses,
                m.total_sat_calls, m.total_decisions, m.total_propagations, m.total_backtracks,
                m.reasoning_steps, m.reveal_waves, f"{m.encode_time_ms:.2f}",
                f"{m.solve_time_ms:.2f}", f"{m.total_runtime_ms:.2f}", m.outcome.value
            ])


def export_to_latex(metrics: list[PuzzleMetrics], output_path: str | Path) -> None:
    """Xuất danh sách chỉ số ra bảng mã nguồn LaTeX tiêu chuẩn cho báo cáo."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    lines: list[str] = [
        r"\begin{table}[htbp]",
        r"\centering",
        r"\caption{Thống kê kết quả thực nghiệm Griductive Solver}",
        r"\begin{tabular}{|l|c|r|r|r|r|r|r|c|}",
        r"\hline",
        r"\textbf{ID} & \textbf{Size} & \textbf{Vars} & \textbf{Clauses} & \textbf{SAT Calls} & \textbf{Decisions} & \textbf{Steps} & \textbf{Time (ms)} & \textbf{Outcome} \\",
        r"\hline",
    ]
    for m in metrics:
        total_v = m.primary_vars + m.aux_vars
        lines.append(
            f"{m.puzzle_id} & {m.grid_size}x{m.grid_size} & {total_v} & {m.clauses} & "
            f"{m.total_sat_calls} & {m.total_decisions} & {m.reasoning_steps} & "
            f"{m.total_runtime_ms:.1f} & {m.outcome.value} \\\\"
        )
    lines.extend([
        r"\hline",
        r"\end{tabular}",
        r"\end{table}",
    ])

    with open(p, mode="w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def plot_runtime_chart(metrics: list[PuzzleMetrics], output_path: str | Path) -> None:
    """Vẽ biểu đồ thời gian chạy và lưu file ảnh."""
    # TODO (Ngọc Quang): Sử dụng matplotlib vẽ biểu đồ thời gian chạy nếu có thư viện
    pass
