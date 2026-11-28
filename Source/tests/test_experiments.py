"""Unit tests for experiment benchmark and export utilities.

Tác dụng:
    Kiểm thử quy trình đo đạc thực nghiệm:
    - run_benchmark_on_puzzle: thu thập đầy đủ 6 nhóm số liệu.
    - export_to_csv: xuất file CSV đúng định dạng.
    - export_to_latex: xuất bảng LaTeX hợp lệ.
    - plot_runtime_chart: xuất file ảnh/SVG biểu đồ.

Người phụ trách: Ngọc Quang (Agent, Experiments & Reviewer 2).
"""

import tempfile
from pathlib import Path
from griductive.experiments.export import export_to_csv, export_to_latex, plot_runtime_chart
from griductive.experiments.runner import run_benchmark_on_puzzle
from griductive.domain.types import SolveStatus


def test_benchmark_runner_on_example_puzzle() -> None:
    """Kiểm tra benchmark runner trên puzzle mẫu 3x3."""
    puzzle_path = Path(__file__).resolve().parent.parent / "puzzles" / "json_example.json"
    metrics = run_benchmark_on_puzzle(puzzle_path)

    # 1. Encoding
    assert metrics.primary_vars == 9
    assert metrics.clauses > 0

    # 2. SAT & DPLL
    assert metrics.total_sat_calls > 0
    assert metrics.total_propagations > 0

    # 3. Agent & Runtime
    assert metrics.reasoning_steps == 8
    assert metrics.total_runtime_ms > 0
    assert metrics.outcome == SolveStatus.SOLVED


def test_export_utilities() -> None:
    """Kiểm tra việc xuất CSV, LaTeX và biểu đồ SVG."""
    puzzle_path = Path(__file__).resolve().parent.parent / "puzzles" / "json_example.json"
    metrics = [run_benchmark_on_puzzle(puzzle_path)]

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = Path(tmp_dir)

        csv_file = tmp_path / "test_metrics.csv"
        export_to_csv(metrics, csv_file)
        assert csv_file.exists()
        content = csv_file.read_text(encoding="utf-8")
        assert "Puzzle ID,Size,Primary Vars" in content
        assert "json-example-3x3" in content

        tex_file = tmp_path / "test_metrics.tex"
        export_to_latex(metrics, tex_file)
        assert tex_file.exists()
        tex_content = tex_file.read_text(encoding="utf-8")
        assert r"\begin{table}" in tex_content
        assert "json-example-3x3" in tex_content

        svg_file = tmp_path / "test_chart.svg"
        plot_runtime_chart(metrics, svg_file)
        assert svg_file.exists()
        svg_content = svg_file.read_text(encoding="utf-8")
        assert "<svg" in svg_content
