"""Entry point for the Griductive Solver application.

Tác dụng:
    Điểm khởi chạy chính của ứng dụng. Hỗ trợ chạy Desktop PyQt6 GUI mặc định,
    hoặc chạy chế độ dòng lệnh (CLI / Experiments / Validation).

Input:
    Tham số dòng lệnh (sys.argv).

Output:
    Mã thoát ứng dụng (exit code int).

Người phụ trách: Trần Văn Nguyên (Leader / Domain & Integrator).
"""

import sys
import argparse


def parse_arguments() -> argparse.Namespace:
    """Xử lý các tham số dòng lệnh."""
    parser = argparse.ArgumentParser(
        description="Griductive Solver - Trợ lý và bộ giải suy diễn logic thông minh."
    )
    parser.add_argument(
        "--cli", action="store_true", help="Chạy ở chế độ dòng lệnh (CLI mode) thay vì Desktop GUI."
    )
    parser.add_argument(
        "--puzzle", type=str, default=None, help="Đường dẫn đến file puzzle JSON cần giải hoặc kiểm tra."
    )
    parser.add_argument(
        "--validate", action="store_true", help="Kiểm tra tính duy nhất (uniqueness) và khả năng giải được."
    )
    return parser.parse_args()


def main() -> int:
    """Khởi động ứng dụng Griductive Solver."""
    args = parse_arguments()

    if args.validate and args.puzzle:
        from griductive.experiments.validate_puzzle import validate_puzzle_file
        valid, msg = validate_puzzle_file(args.puzzle)
        print(f"Validation result for {args.puzzle}: {'VALID' if valid else 'INVALID'}\n{msg}")
        return 0 if valid else 1

    if args.cli:
        print("Chế độ CLI chưa kích hoạt. Vui lòng chạy GUI hoặc dùng --validate.")
        return 0

    # Khởi chạy Desktop PyQt6 GUI
    try:
        from griductive.gui.app import run_gui
        return run_gui()
    except ImportError as e:
        print(f"Lỗi khởi chạy GUI (hãy đảm bảo đã cài requirements.txt và PyQt6): {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
