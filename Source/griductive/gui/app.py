"""Main PyQt6 Application Window.

Tác dụng:
    Cửa sổ chính của ứng dụng Desktop PyQt6:
    - Ghép nối BoardView, CluePanel, ControlPanel và thanh trạng thái (StatusBar).
    - Sở hữu đối tượng GameSession duy nhất (không trực tiếp tương tác với Engine hay DPLL).
    - Điều phối luồng sự kiện:
        + Load: QFileDialog -> session.load_puzzle() -> cập nhật UI.
        + Restart: session.restart() -> cập nhật UI.
        + Chơi tay: click thẻ úp -> chọn CRIMINAL/INNOCENT -> session.submit_verdict() -> báo ACCEPTED / NOT_PROVABLE / CONTRADICTED / ALREADY_REVEALED.
        + Hint: session.hint() -> hiển thị popup gợi ý, clue liên quan và highlight ô.
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
    QLabel,
    QMainWindow,
    QMessageBox,
    QVBoxLayout,
    QWidget,
)
from griductive.agent.logic_agent import AutoSolveStep
from griductive.app.session import GameSession
from griductive.domain.errors import GriductiveError
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState
from griductive.domain.types import SolveStatus, Status, VerdictResult
from griductive.gui.board_view import BoardView
from griductive.gui.clue_panel import CluePanel, format_clue_description
from griductive.gui.controls import DEFAULT_STEP_DELAY_MS, ControlPanel

_STATUS_TEXT = {
    SolveStatus.RUNNING: "Đang chơi",
    SolveStatus.SOLVED: "Đã giải xong",
    SolveStatus.STUCK: "Bị kẹt: không còn ô nào suy ra được",
    SolveStatus.INCONSISTENT: "Cơ sở tri thức MÂU THUẪN",
    SolveStatus.TIMEOUT: "Hết thời gian suy diễn",
}

_REJECT_TITLES = {
    VerdictResult.NOT_PROVABLE: "NOT_PROVABLE – Chưa đủ dữ kiện",
    VerdictResult.CONTRADICTED: "CONTRADICTED – Logic ép ngược lại",
    VerdictResult.ALREADY_REVEALED: "ALREADY_REVEALED – Ô đã lật",
}


class MainWindow(QMainWindow):
    """Cửa sổ ứng dụng chính của Griductive Solver."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Griductive Solver - Trợ lý suy diễn logic")
        self.resize(1100, 760)

        self.session = GameSession()

        # Layout chính
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        self.status_label = QLabel("Chưa nạp puzzle. Bấm “Tải Puzzle” để bắt đầu.", self)
        main_layout.addWidget(self.status_label)

        content_layout = QHBoxLayout()
        self.board_view = BoardView(self)
        self.clue_panel = CluePanel(self)
        content_layout.addWidget(self.board_view, stretch=3)
        content_layout.addWidget(self.clue_panel, stretch=2)

        self.control_panel = ControlPanel(self)
        main_layout.addLayout(content_layout)
        main_layout.addWidget(self.control_panel)

        # Kết nối sự kiện giữa các widget
        self.clue_panel.clue_selected.connect(self._on_clue_selected)
        self.board_view.cell_submitted.connect(self._on_cell_submitted)
        self.control_panel.load_requested.connect(self._on_load_puzzle)
        self.control_panel.restart_requested.connect(self._on_restart)
        self.control_panel.hint_requested.connect(self._on_hint)
        self.control_panel.auto_solve_requested.connect(self._on_auto_solve)
        self.control_panel.stop_requested.connect(self._stop_auto_solve)
        self.control_panel.speed_changed.connect(self._on_speed_changed)

        self._auto_solve_gen = None
        self._last_auto_step: AutoSolveStep | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(DEFAULT_STEP_DELAY_MS)
        self._timer.timeout.connect(self._on_auto_solve_tick)

    # ------------------------------------------------------------ helpers
    def _show_state(self, state: PublicState, new_owner: Coord | None = None) -> None:
        """Vẽ lại bàn cờ, danh sách clue và nhãn trạng thái từ một PublicState."""
        self.board_view.update_board(state)
        self.clue_panel.set_clues(state.revealed_clues)
        self.clue_panel.select_owner(new_owner)
        revealed = sum(1 for c in state.cells if c.revealed)
        self.status_label.setText(
            f"Puzzle {state.puzzle_id} ({state.size}x{state.size}) – "
            f"đã lật {revealed}/{len(state.cells)} ô – "
            f"{_STATUS_TEXT.get(state.solve_status, state.solve_status.value)}"
        )

    def _reset_highlights(self) -> None:
        self.board_view.clear_highlights()

    # ------------------------------------------------------------- events
    def _on_load_puzzle(self) -> None:
        """Mở hộp thoại chọn file puzzle JSON."""
        default_dir = str(Path(__file__).resolve().parent.parent.parent / "puzzles")
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn file Puzzle", default_dir, "JSON Files (*.json)"
        )
        if not file_path:
            return
        self._stop_auto_solve()
        try:
            state = self.session.load_puzzle(file_path)
        except GriductiveError as e:
            QMessageBox.critical(self, "Lỗi nạp file", f"Không thể nạp puzzle: {e}")
            return
        except Exception as e:  # noqa: BLE001 - JSON/IO lỗi bất ngờ không được làm sập GUI
            QMessageBox.critical(self, "Lỗi nạp file", f"Không thể nạp puzzle: {e}")
            return
        self._reset_highlights()
        self._show_state(state)
        self.statusBar().showMessage(f"Đã nạp puzzle: {state.puzzle_id}", 5000)

    def _on_restart(self) -> None:
        """Chơi lại từ đầu (khôi phục KB_0)."""
        if not self.session.has_active_game:
            return
        self._stop_auto_solve()
        state = self.session.restart()
        self._reset_highlights()
        self._show_state(state)
        self.statusBar().showMessage("Đã khôi phục bàn cờ về ban đầu.", 3000)

    def _on_clue_selected(self, cells: tuple[Coord, ...]) -> None:
        self.board_view.mark_hint(None)
        self.board_view.highlight_cells(cells)

    def _on_cell_submitted(self, cell: Coord, status: Status) -> None:
        """Người chơi gọi CRIMINAL/INNOCENT cho một ô."""
        if not self.session.has_active_game or self.control_panel.is_auto_running:
            return
        try:
            outcome = self.session.submit_verdict(cell, status)
        except GriductiveError as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            return

        if outcome.result == VerdictResult.ACCEPTED:
            self._reset_highlights()
            self._show_state(outcome.public_state, new_owner=outcome.cell)
            if outcome.revealed_clue is not None:
                self.board_view.highlight_cells(outcome.revealed_clue.cells())
            self.statusBar().showMessage(outcome.message, 5000)
            if outcome.public_state.solve_status == SolveStatus.SOLVED or outcome.public_state.is_all_revealed():
                QMessageBox.information(self, "Hoàn thành", "Bạn đã giải xong puzzle!")
            return

        # Bị từ chối: trạng thái game không đổi, không lộ clue ẩn.
        self._show_state(outcome.public_state)
        self.statusBar().showMessage(outcome.message, 6000)
        title = _REJECT_TITLES.get(outcome.result, outcome.result.value)
        QMessageBox.warning(self, title, outcome.message)

    def _on_hint(self) -> None:
        """Hiện gợi ý: ô chứng minh được tiếp theo và các clue làm căn cứ."""
        if not self.session.has_active_game:
            return
        hint = self.session.hint()
        if hint is None:
            QMessageBox.information(self, "Gợi ý", "Chưa có ô nào bị ép buộc logic để gợi ý.")
            return
        related = self.clue_panel.find_clues(hint.related_clue_ids)
        lines = [f"Ô {hint.cell} chắc chắn là {hint.suggested_status.value}."]
        if related:
            lines.append("")
            lines.append("Căn cứ từ các manh mối đã mở:")
            lines.extend(f"• {format_clue_description(c)}" for c in related)
        else:
            lines.append("")
            lines.append("Suy ra từ tổ hợp các manh mối đã mở.")
        highlighted: set[Coord] = set()
        for clue in related:
            highlighted.update(clue.cells())
        self.board_view.highlight_cells(tuple(highlighted))
        self.board_view.mark_hint(hint.cell)
        QMessageBox.information(self, "Gợi ý", "\n".join(lines))

    # ---------------------------------------------------------- auto solve
    def _on_speed_changed(self, delay_ms: int) -> None:
        self._timer.setInterval(delay_ms)

    def _on_auto_solve(self) -> None:
        """Bắt đầu chạy tự động giải qua timer."""
        if not self.session.has_active_game or self.control_panel.is_auto_running:
            return
        try:
            self._auto_solve_gen = self.session.auto_solve_steps()
        except GriductiveError as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            return
        self._last_auto_step = None
        self._reset_highlights()
        self.control_panel.set_auto_running(True)
        self.board_view.set_input_enabled(False)
        self._timer.start(self.control_panel.step_delay_ms)

    def _stop_auto_solve(self) -> None:
        """Dừng Auto Solve (nếu đang chạy) và trả giao diện về chế độ chơi tay."""
        self._timer.stop()
        self._auto_solve_gen = None
        self.control_panel.set_auto_running(False)
        self.board_view.set_input_enabled(True)

    def _on_auto_solve_tick(self) -> None:
        """Thực thi một bước giải tự động."""
        if self._auto_solve_gen is None:
            self._stop_auto_solve()
            return
        try:
            step = next(self._auto_solve_gen)
        except StopIteration:
            self._finish_auto_solve()
            return
        except GriductiveError as e:
            self._stop_auto_solve()
            QMessageBox.critical(self, "Lỗi giải tự động", str(e))
            return

        self._last_auto_step = step
        cell = step.step.cell if step.step is not None else None
        self._show_state(step.public_state, new_owner=cell)
        if step.step is not None:
            self.board_view.highlight_cells((step.step.cell,))
            self.statusBar().showMessage(
                f"Bước {step.step.step} (wave {step.step.wave}): "
                f"{step.step.cell} là {step.step.classification.value}",
                5000,
            )

    def _finish_auto_solve(self) -> None:
        """Generator đã hết: báo kết thúc theo trạng thái cuối của SolveTrace."""
        last = self._last_auto_step
        self._stop_auto_solve()
        if last is None:
            self.statusBar().showMessage("Không có bước giải nào.", 5000)
            return
        final_status = last.trace.solve_status
        text = _STATUS_TEXT.get(final_status, final_status.value)
        self.status_label.setText(self.status_label.text().rsplit(" – ", 1)[0] + f" – {text}")
        self.statusBar().showMessage(f"Giải tự động kết thúc: {text}", 8000)
        if final_status != SolveStatus.SOLVED:
            QMessageBox.information(self, "Giải tự động dừng", text)


def run_gui() -> int:
    """Khởi tạo và chạy vòng lặp ứng dụng Qt."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
