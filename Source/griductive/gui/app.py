"""Main PyQt6 Application Window.

Tác dụng:
    Cửa sổ chính của ứng dụng Desktop PyQt6:
    - Ghép nối BoardView, CluePanel, ControlPanel và thanh trạng thái (StatusBar).
    - Sở hữu đối tượng GameSession duy nhất (không trực tiếp tương tác với Engine hay DPLL).
    - Điều phối luồng sự kiện:
        + Load: QFileDialog -> session.load_puzzle() -> cập nhật UI.
        + Restart: session.restart() -> cập nhật UI.
        + Hint: session.hint() -> hiển thị popup gợi ý và highlight ô.
        + Auto Solve: dùng QTimer duyệt generator session.auto_solve_steps() để cập nhật từng bước mượt mà.

Input:
    Các sự kiện người dùng và cập nhật từ GameSession.

Output:
    Mã thoát ứng dụng (int).

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

import sys
from pathlib import Path
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from griductive.app.session import GameSession
from griductive.gui.board_view import BoardView
from griductive.gui.clue_panel import CluePanel
from griductive.gui.controls import ControlPanel


class MainWindow(QMainWindow):
    """Cửa sổ ứng dụng chính của Griductive Solver."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Griductive Solver - Trợ lý suy diễn logic")
        self.resize(1000, 700)

        self.session = GameSession()

        # Layout chính
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        content_layout = QHBoxLayout()
        self.board_view = BoardView(self)
        self.clue_panel = CluePanel(self)
        content_layout.addWidget(self.board_view, stretch=3)
        content_layout.addWidget(self.clue_panel, stretch=2)

        self.control_panel = ControlPanel(self)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.control_panel)

        # Kết nối sự kiện giữa các widget
        self.clue_panel.clue_selected.connect(self.board_view.highlight_cells)
        self.control_panel.load_requested.connect(self._on_load_puzzle)
        self.control_panel.restart_requested.connect(self._on_restart)
        self.control_panel.hint_requested.connect(self._on_hint)
        self.control_panel.auto_solve_requested.connect(self._on_auto_solve)

        self._auto_solve_gen = None
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._on_auto_solve_tick)

    def _on_load_puzzle(self) -> None:
        """Mở hộp thoại chọn file puzzle JSON."""
        default_dir = str(Path(__file__).resolve().parent.parent.parent / "puzzles")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Puzzle", default_dir, "JSON Files (*.json)"
        )
        if file_path:
            try:
                state = self.session.load_puzzle(file_path)
                self.board_view.update_board(state)
                self.clue_panel.set_clues(state.revealed_clues)
                self.statusBar().showMessage(f"Đã nạp puzzle: {state.puzzle_id}", 5000)
            except Exception as e:
                QMessageBox.critical(self, "Lỗi nạp file", f"Không thể nạp puzzle: {e}")

    def _on_restart(self) -> None:
        """Chơi lại từ đầu."""
        if self.session.has_active_game:
            state = self.session.restart()
            self.board_view.update_board(state)
            self.clue_panel.set_clues(state.revealed_clues)
            self.statusBar().showMessage("Đã khôi phục bàn cờ về ban đầu.", 3000)

    def _on_hint(self) -> None:
        """Hiện gợi ý."""
        hint = self.session.hint()
        if hint:
            QMessageBox.information(
                self, "Gợi ý", f"Ô {hint.cell} chắc chắn là {hint.suggested_status.value}!"
            )
        else:
            QMessageBox.information(self, "Gợi ý", "Chưa có ô nào bị ép buộc logic để gợi ý.")

    def _on_auto_solve(self) -> None:
        """Bắt đầu chạy tự động giải qua timer."""
        if not self.session.has_active_game:
            return
        self._auto_solve_gen = self.session.auto_solve_steps()
        self._timer.start(500)  # 500ms mỗi bước

    def _on_auto_solve_tick(self) -> None:
        """Thực thi một bước giải tự động."""
        if not self._auto_solve_gen:
            self._timer.stop()
            return
        try:
            step = next(self._auto_solve_gen)
            self.board_view.update_board(step.public_state)
            self.clue_panel.set_clues(step.public_state.revealed_clues)
        except StopIteration:
            self._timer.stop()
            self._auto_solve_gen = None
            self.statusBar().showMessage("Hoàn tất giải tự động!", 5000)


def run_gui() -> int:
    """Khởi tạo và chạy vòng lặp ứng dụng Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
