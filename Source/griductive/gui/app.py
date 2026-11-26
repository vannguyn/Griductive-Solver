"""Main Application Window for Grid Detective.

Tác dụng:
    Cửa sổ chính của ứng dụng Desktop Grid Detective:
    - Bố cục trung tâm tuyệt đối theo layout Desktop Puzzle Game hiện đại:
        + HeaderBar: Logo, bộ chọn Daily Case / Level, chỉ số vụ án.
        + Board Area: Bàn cờ căn giữa với thẻ nhân vật vector minh họa.
        + Clue Banner: Dải băng hiển thị manh mối / suy luận trọng tâm.
        + BottomBar: Các nút chức năng [ GHI CHÚ ], [ GỢI Ý ], [ TỰ ĐỘNG GIẢI ], [ CHƠI LẠI ].
    - Quản lý phiên chơi qua GameSession facade duy nhất (tuân thủ Rule 1 & Rule 2).
    - Xử lý các tương tác: Thẩm vấn phán quyết, lật thẻ 3D, rung lắc phản hồi, spotlight manh mối.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

import sys
from pathlib import Path

from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QColor, QFont, QPalette
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)
from griductive.agent.logic_agent import AutoSolveStep
from griductive.app.session import GameSession
from griductive.clues.base import Clue
from griductive.domain.errors import GriductiveError
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicState
from griductive.domain.types import SolveStatus, Status, VerdictResult
from griductive.gui.board_view import BoardView
from griductive.gui.card_widget import FLIP_DURATION_MS
from griductive.gui.clue_panel import CluePanel, format_clue_description
from griductive.gui.controls import (
    DEFAULT_STEP_DELAY_MS,
    BottomBar,
    ClueBanner,
    ControlPanel,
    HeaderBar,
)

_STATUS_TEXT = {
    SolveStatus.RUNNING: "Đang điều tra",
    SolveStatus.SOLVED: "Vụ án đã phá thành công!",
    SolveStatus.STUCK: "Bị kẹt: Chưa đủ dữ kiện",
    SolveStatus.INCONSISTENT: "Mâu thuẫn dữ kiện logic",
    SolveStatus.TIMEOUT: "Hết thời gian suy diễn",
}


class MainWindow(QMainWindow):
    """Cửa sổ ứng dụng chính của trò chơi trinh thám Grid Detective."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Grid Detective")
        self.resize(1440, 900)
        self.setMinimumSize(1100, 700)

        # Bảng màu Dark Cozy Editorial cho toàn bộ cửa sổ
        self.setStyleSheet("""
            QMainWindow {
                background-color: #12151D;
            }
            QScrollArea {
                background-color: transparent;
                border: none;
            }
            QScrollBar:vertical, QScrollBar:horizontal {
                background: #161A22;
                border: none;
                width: 8px;
                height: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {
                background: #2D3748;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:hover {
                background: #4A5568;
            }
        """)

        self.session = GameSession()

        # Layout chính
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. HeaderBar trên cùng
        self.header_bar = HeaderBar(self)
        main_layout.addWidget(self.header_bar)

        # 2. Vùng trung tâm: Bàn cờ đặt trong ScrollArea căn giữa hoàn hảo
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        board_container = QWidget()
        board_container.setStyleSheet("background-color: transparent;")
        board_layout = QVBoxLayout(board_container)
        board_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        board_layout.setContentsMargins(20, 20, 20, 10)

        self.board_view = BoardView(board_container)
        board_layout.addWidget(self.board_view)
        scroll_area.setWidget(board_container)
        main_layout.addWidget(scroll_area, stretch=1)

        # 3. Dải băng Manh mối & Suy luận trọng tâm (ClueBanner)
        banner_container = QWidget(self)
        banner_layout = QVBoxLayout(banner_container)
        banner_layout.setContentsMargins(40, 0, 40, 10)
        self.clue_banner = ClueBanner(banner_container)
        banner_layout.addWidget(self.clue_banner)
        main_layout.addWidget(banner_container)

        # 4. Thanh điều khiển hành động dưới cùng (BottomBar)
        self.bottom_bar = BottomBar(self)
        main_layout.addWidget(self.bottom_bar)

        # CluePanel chỉ giữ dữ liệu clue cho Hint và xử lý spotlight khi click
        # vào thẻ đã mở; không hiển thị thành một vùng panel riêng trên GUI.
        self.clue_panel = CluePanel(self)
        self.clue_panel.hide()
        self.control_panel = ControlPanel(self)
        self.control_panel.hide()

        # Kết nối sự kiện
        self.header_bar.level_selected.connect(self._on_preset_level_selected)
        self.board_view.cell_submitted.connect(self._on_cell_submitted)
        self.board_view.cell_inspected.connect(self._on_cell_inspected)
        self.bottom_bar.restart_requested.connect(self._on_restart)
        self.bottom_bar.hint_requested.connect(self._on_hint)
        self.bottom_bar.auto_solve_requested.connect(self._on_auto_solve)
        self.bottom_bar.stop_requested.connect(self._stop_auto_solve)
        self.bottom_bar.speed_changed.connect(self._on_speed_changed)

        self._auto_solve_gen = None
        self._last_auto_step: AutoSolveStep | None = None
        self._timer = QTimer(self)
        self._timer.setInterval(DEFAULT_STEP_DELAY_MS)
        self._timer.timeout.connect(self._on_auto_solve_tick)
        self._current_spotlight_owner: Coord | None = None
        self._victory_epoch = 0
        self._manual_step_count = 0

        # Tự động nạp màn Tutorial mẫu khi khởi động để trải nghiệm ngay
        self._on_preset_level_selected("3x3/tutorial.json")

    # ------------------------------------------------------------ Helpers
    def _show_state(self, state: PublicState, new_owner: Coord | None = None) -> None:
        """Vẽ lại bàn cờ, cập nhật danh sách manh mối và nhãn trạng thái."""
        self.bottom_bar.set_game_active(True)
        self.control_panel.set_game_active(True)
        self.board_view.update_board(state)
        self.clue_panel.set_clues(state.revealed_clues)
        self.clue_panel.select_owner(new_owner)

        revealed_count = sum(1 for c in state.cells if c.revealed)
        total_cells = len(state.cells)
        self.header_bar.set_status_text(f"● ĐÃ LẬT: {revealed_count} / {total_cells}")

        # Cập nhật banner nếu có clue mới vừa lật
        if new_owner is not None:
            clue = self._find_clue(new_owner)
            if clue is not None:
                cell_info = next((c for c in state.cells if c.coord == new_owner), None)
                name = cell_info.name if cell_info else ""
                job = cell_info.job if cell_info else ""
                self.clue_banner.display_clue(clue, name, job)
                self.board_view.spotlight_clue(subject=clue.owner, targets=clue.cells())
                self._current_spotlight_owner = clue.owner
            else:
                self._reset_highlights()

    def _schedule_victory_dialog(self, steps: int) -> None:
        """Hiển thị duy nhất một thông báo hoàn tất sau hiệu ứng lật thẻ cuối."""
        epoch = self._victory_epoch

        def _show() -> None:
            if epoch == self._victory_epoch:
                QMessageBox.information(
                    self,
                    "VỤ ÁN HOÀN TẤT!",
                    f"Đã giải xong trong {steps} bước suy luận.",
                )

        QTimer.singleShot(FLIP_DURATION_MS + 60, _show)

    def _reset_highlights(self) -> None:
        self._current_spotlight_owner = None
        self.board_view.clear_highlights()
        self.clue_banner.display_clue(None)

    def _find_clue(self, owner: Coord) -> Clue | None:
        for c in self.clue_panel.clues():
            if c.owner == owner:
                return c
        return None

    # ------------------------------------------------------------- Events
    def _on_preset_level_selected(self, rel_path: str) -> None:
        """Nạp vụ án từ bộ chọn danh sách level nhanh."""
        file_path = Path(__file__).resolve().parent.parent.parent / "puzzles" / rel_path
        if not file_path.exists():
            return
        self._stop_auto_solve()
        try:
            state = self.session.load_puzzle(file_path)
        except Exception as e:
            QMessageBox.critical(self, "Lỗi nạp vụ án", str(e))
            return

        self._victory_epoch += 1
        self._manual_step_count = 0
        self._reset_highlights()
        self._show_state(state)

    def _on_restart(self) -> None:
        """Khôi phục bàn cờ về trạng thái khởi đầu (KB_0)."""
        if not self.session.has_active_game:
            return
        self._stop_auto_solve()
        self._victory_epoch += 1
        self._manual_step_count = 0
        state = self.session.restart()
        self._reset_highlights()
        self._show_state(state)
        self.statusBar().showMessage("Đã khôi phục vụ án về hiện trường ban đầu.", 3000)

    def _on_cell_inspected(self, coord: Coord) -> None:
        """Người chơi click vào thẻ đã giải để xem manh mối (Spotlight Clue)."""
        # Nếu đang xem đúng clue của thẻ này -> toggle tắt spotlight
        if self._current_spotlight_owner == coord:
            self._reset_highlights()
            return

        clue = self._find_clue(coord)
        if clue is not None:
            self._current_spotlight_owner = coord
            cell_info = next((c for c in self.session._engine.public_state().cells if c.coord == coord), None)  # type: ignore
            name = cell_info.name if cell_info else ""
            job = cell_info.job if cell_info else ""
            self.clue_banner.display_clue(clue, name, job)
            self.board_view.spotlight_clue(subject=clue.owner, targets=clue.cells())
        else:
            self._reset_highlights()

    def _on_clue_selected(self, cells: tuple[Coord, ...]) -> None:
        """Highlight các ô được clue chọn trong CluePanel tham chiếu."""
        self._current_spotlight_owner = None
        self.clue_banner.display_message(
            "CLUE ĐÃ CHỌN",
            "Các ô liên quan đã được tô sáng trên bàn cờ.",
        )
        self.board_view.highlight_cells(cells)

    def _on_cell_submitted(self, cell: Coord, status: Status) -> None:
        """Người chơi đưa ra phán quyết về một nghi phạm."""
        if not self.session.has_active_game or self.bottom_bar.is_auto_running:
            return

        try:
            outcome = self.session.submit_verdict(cell, status)
        except GriductiveError as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            return

        if outcome.result == VerdictResult.ACCEPTED:
            self._manual_step_count += 1
            self._show_state(outcome.public_state, new_owner=outcome.cell)
            self.statusBar().showMessage(outcome.message, 4000)
            if outcome.public_state.solve_status == SolveStatus.SOLVED or outcome.public_state.is_all_revealed():
                self._schedule_victory_dialog(self._manual_step_count)
            return

        # Phán quyết bị từ chối: rung lắc thẻ và hiển thị phản hồi trên banner
        self.board_view.shake_cell(cell)
        if outcome.result == VerdictResult.NOT_PROVABLE:
            title = "CHƯA ĐỦ BẰNG CHỨNG"
        elif outcome.result == VerdictResult.INCONSISTENT:
            title = "MÂU THUẪN LOGIC"
        else:
            title = "PHÁN QUYẾT BỊ BÁC"
        self.clue_banner.display_message(title, outcome.message, is_warning=True)
        self.statusBar().showMessage(outcome.message, 5000)

    def _on_hint(self) -> None:
        """Đưa ra gợi ý bước đi ép buộc logic tiếp theo."""
        if not self.session.has_active_game:
            return

        hint = self.session.hint()
        if hint is None:
            self.clue_banner.display_message("GỢI Ý", "Chưa có ô nào bị ép buộc logic ở thời điểm hiện tại.")
            return

        related = self.clue_panel.find_clues(hint.related_clue_ids)
        msg = f"Ô {hint.cell} chắc chắn là {hint.suggested_status.value}."
        if related:
            msg += f" Căn cứ từ: {format_clue_description(related[0])}"

        self.clue_banner.display_message("GỢI Ý SUY LUẬN", msg)
        self.board_view.mark_hint(hint.cell)

    # ---------------------------------------------------------- Auto Solve
    def _on_speed_changed(self, delay_ms: int) -> None:
        self._timer.setInterval(delay_ms)

    def _on_auto_solve(self) -> None:
        """Bắt đầu chạy tự động giải qua QTimer."""
        if not self.session.has_active_game or self.bottom_bar.is_auto_running:
            return

        try:
            self._auto_solve_gen = self.session.auto_solve_steps()
        except GriductiveError as e:
            QMessageBox.critical(self, "Lỗi", str(e))
            return

        self._last_auto_step = None
        self._reset_highlights()
        self.bottom_bar.set_auto_running(True)
        self.control_panel.set_auto_running(True)
        self.board_view.set_input_enabled(False)
        self._timer.start(self.bottom_bar.step_delay_ms)

    def _stop_auto_solve(self) -> None:
        """Dừng Auto Solve và trả quyền điều khiển cho người chơi."""
        self._timer.stop()
        self._auto_solve_gen = None
        self.bottom_bar.set_auto_running(False)
        self.control_panel.set_auto_running(False)
        self.board_view.set_input_enabled(True)

    def _on_auto_solve_tick(self) -> None:
        """Thực thi một bước giải tự động trên timer."""
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

    def _finish_auto_solve(self) -> None:
        """Hoàn tất quá trình giải tự động."""
        last = self._last_auto_step
        self._stop_auto_solve()
        if last is None:
            return

        final_status = last.trace.solve_status
        text = _STATUS_TEXT.get(final_status, final_status.value)
        self.header_bar.set_status_text(f"● {text.upper()}")

        if final_status == SolveStatus.SOLVED:
            self._schedule_victory_dialog(len(last.trace.steps))
        else:
            QMessageBox.information(self, "Tự động giải kết thúc", text)


def run_gui() -> int:
    """Khởi tạo và chạy ứng dụng Grid Detective."""
    # Phải đặt font mặc định trước khi QApplication tạo các widget nội bộ.
    # Một số bản Qt trên Windows khởi tạo font hệ thống ở dạng pixel-size,
    # khiến pointSize() trả về -1; nếu giá trị này bị dùng lại như point size,
    # Qt sẽ phát cảnh báo QFont::setPointSize.
    QApplication.setFont(QFont("Segoe UI", 10))

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Bảo đảm cả trường hợp QApplication đã tồn tại (ví dụ khi chạy từ IDE).
    app.setFont(QFont("Segoe UI", 10))

    window = MainWindow()
    window.show()
    return app.exec()
