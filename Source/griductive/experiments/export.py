"""Export utilities for experiment benchmark metrics (CSV, LaTeX, plots).

Tác dụng:
    Xuất các số liệu thực nghiệm thu thập được thành:
    - File CSV (Source/results/metrics.csv) phục vụ phân tích.
    - Bảng LaTeX (Source/results/metrics.tex) dán trực tiếp vào Final Report (30 điểm).
    - Biểu đồ thời gian chạy theo kích thước lưới (runtime_by_grid.svg / .png).

Input:
    list[PuzzleMetrics] và đường dẫn file xuất.

Output:
    Các file CSV, TEX, SVG/PNG được ghi vào đĩa.

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


def generate_svg_chart(metrics: list[PuzzleMetrics], output_path: Path) -> None:
    """Tạo biểu đồ dạng SVG vector độc lập không cần thư viện bên ngoài."""
    width = 800
    height = 450
    margin_left = 100
    margin_bottom = 80
    margin_top = 60
    margin_right = 40

    plot_width = width - margin_left - margin_right
    plot_height = height - margin_top - margin_bottom

    if not metrics:
        max_time = 10.0
    else:
        max_time = max(m.total_runtime_ms for m in metrics)
        if max_time <= 0:
            max_time = 10.0
        max_time *= 1.2  # Thêm khoảng đệm 20%

    n = len(metrics)
    bar_width = min(40, (plot_width // max(1, n)) - 10)

    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        '<style>',
        '  .title { font-family: sans-serif; font-size: 18px; font-weight: bold; fill: #1e293b; text-anchor: middle; }',
        '  .axis { stroke: #64748b; stroke-width: 1.5; }',
        '  .grid { stroke: #e2e8f0; stroke-width: 1; stroke-dasharray: 4,4; }',
        '  .label { font-family: sans-serif; font-size: 11px; fill: #475569; }',
        '  .bar-3 { fill: #3b82f6; }',
        '  .bar-4 { fill: #10b981; }',
        '  .bar-5 { fill: #f59e0b; }',
        '  .val { font-family: sans-serif; font-size: 10px; font-weight: bold; fill: #0f172a; text-anchor: middle; }',
        '</style>',
        f'<text class="title" x="{width // 2}" y="35">Griductive Solver - Thời gian thực thi theo Puzzle (ms)</text>',
    ]

    # Trục Y và Grid lines
    num_y_ticks = 5
    for i in range(num_y_ticks + 1):
        y_val = (max_time / num_y_ticks) * i
        y_pos = margin_top + plot_height - (plot_height * (i / num_y_ticks))
        svg_parts.append(f'<line class="grid" x1="{margin_left}" y1="{y_pos}" x2="{width - margin_right}" y2="{y_pos}" />')
        svg_parts.append(f'<text class="label" x="{margin_left - 10}" y="{y_pos + 4}" text-anchor="end">{y_val:.1f}</text>')

    # Trục toạ độ X, Y
    svg_parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top + plot_height}" x2="{width - margin_right}" y2="{margin_top + plot_height}" />')
    svg_parts.append(f'<line class="axis" x1="{margin_left}" y1="{margin_top}" x2="{margin_left}" y2="{margin_top + plot_height}" />')

    # Vẽ từng cột
    step_x = plot_width / max(1, n)
    for idx, m in enumerate(metrics):
        x = margin_left + idx * step_x + (step_x - bar_width) / 2
        bar_h = (m.total_runtime_ms / max_time) * plot_height
        y = margin_top + plot_height - bar_h

        bar_cls = "bar-3" if m.grid_size == 3 else ("bar-4" if m.grid_size == 4 else "bar-5")
        svg_parts.append(f'<rect class="{bar_cls}" x="{x:.1f}" y="{y:.1f}" width="{bar_width}" height="{bar_h:.1f}" rx="3" />')
        svg_parts.append(f'<text class="val" x="{x + bar_width / 2:.1f}" y="{y - 5:.1f}">{m.total_runtime_ms:.1f}</text>')

        # Nhãn X (Tên puzzle ngắn gọn)
        short_id = m.puzzle_id.replace("puzzle-", "").replace("json-example-", "ex-")
        svg_parts.append(
            f'<text class="label" x="{x + bar_width / 2:.1f}" y="{margin_top + plot_height + 20}" '
            f'text-anchor="end" transform="rotate(-35, {x + bar_width / 2:.1f}, {margin_top + plot_height + 20})">{short_id}</text>'
        )

    # Chú thích Legend
    leg_x = width - margin_right - 220
    leg_y = margin_top - 20
    svg_parts.extend([
        f'<rect class="bar-3" x="{leg_x}" y="{leg_y}" width="12" height="12" rx="2" />',
        f'<text class="label" x="{leg_x + 16}" y="{leg_y + 10}">3x3</text>',
        f'<rect class="bar-4" x="{leg_x + 60}" y="{leg_y}" width="12" height="12" rx="2" />',
        f'<text class="label" x="{leg_x + 76}" y="{leg_y + 10}">4x4</text>',
        f'<rect class="bar-5" x="{leg_x + 120}" y="{leg_y}" width="12" height="12" rx="2" />',
        f'<text class="label" x="{leg_x + 136}" y="{leg_y + 10}">5x5</text>',
    ])

    svg_parts.append('</svg>')

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(svg_parts) + "\n")


def plot_runtime_chart(metrics: list[PuzzleMetrics], output_path: str | Path) -> None:
    """Vẽ biểu đồ thời gian chạy (hỗ trợ cả matplotlib nếu có hoặc xuất SVG chuẩn)."""
    p = Path(output_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    # 1. Thử dùng matplotlib nếu môi trường có sẵn
    try:
        import matplotlib.pyplot as plt
        ids = [m.puzzle_id for m in metrics]
        times = [m.total_runtime_ms for m in metrics]
        colors = ['#3b82f6' if m.grid_size == 3 else ('#10b981' if m.grid_size == 4 else '#f59e0b') for m in metrics]

        plt.figure(figsize=(10, 5))
        plt.bar(ids, times, color=colors)
        plt.xlabel("Puzzle ID")
        plt.ylabel("Thời gian (ms)")
        plt.title("Griductive Solver - Thời gian thực thi theo Puzzle")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.savefig(p)
        plt.close()
        return
    except Exception:
        pass

    # 2. Xuất SVG vector chuẩn không phụ thuộc thư viện ngoài
    svg_path = p.with_suffix(".svg")
    generate_svg_chart(metrics, svg_path)
