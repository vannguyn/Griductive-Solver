"""Controls and editorial navigation bars for Grid Detective.

Tác dụng:
    Cung cấp các thanh giao diện theo chuẩn thiết kế desktop puzzle game:
    - HeaderBar: Logo game, bộ chọn Daily Case / Level và trạng thái vụ án.
    - ClueBanner: Dải băng hiển thị manh mối / suy luận trọng tâm bên dưới bàn cờ.
    - BottomBar: Các nút chức năng [ GHI CHÚ ], [ GỢI Ý ], [ TỰ ĐỘNG GIẢI ], [ CHƠI LẠI ].
    - Tương thích 100% với ControlPanel API của MainWindow.
"""

import json
from pathlib import Path
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QComboBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)
from griductive.clues.base import Clue
from griductive.gui.clue_panel import format_clue_description

MIN_STEP_DELAY_MS = 100
MAX_STEP_DELAY_MS = 2000
DEFAULT_STEP_DELAY_MS = 600


class HeaderBar(QWidget):
    """Thanh tiêu đề trên cùng: Logo Grid Detective, Daily Case Selector, Status."""

    load_requested = pyqtSignal()
    level_selected = pyqtSignal(str)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(56)
        self.setStyleSheet("""
            QWidget {
                background-color: #161A22;
                border-bottom: 1px solid #28303F;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 0, 24, 0)
        layout.setSpacing(18)

        # 1. Logo
        logo = QLabel("🔍  GRID DETECTIVE", self)
        logo.setStyleSheet("color: #F8FAFC; font-family: 'Georgia'; font-size: 16px; font-weight: bold; letter-spacing: 2px;")
        layout.addWidget(logo)

        # Đường phân cách
        sep1 = QFrame(self)
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #2D3748;")
        layout.addWidget(sep1)

        # 2. Case Selector (Level Dropdown)
        case_lbl = QLabel("VỤ ÁN:", self)
        case_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold; letter-spacing: 1px;")
        layout.addWidget(case_lbl)

        self.level_combo = QComboBox(self)
        self.level_combo.setStyleSheet("""
            QComboBox {
                background-color: #222834;
                color: #F1F5F9;
                border: 1px solid #3B465A;
                border-radius: 8px;
                padding: 5px 12px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
                min-width: 260px;
            }
            QComboBox:hover {
                border-color: #64748B;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox QAbstractItemView {
                background-color: #1E2430;
                color: #F1F5F9;
                selection-background-color: #334155;
                border: 1px solid #3B465A;
                border-radius: 6px;
                padding: 4px;
            }
        """)
        self._populate_levels()
        self.level_combo.currentIndexChanged.connect(self._on_combo_changed)
        layout.addWidget(self.level_combo)

        self.btn_load = QPushButton("📂  MỞ FILE", self)
        self.btn_load.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_load.setStyleSheet("""
            QPushButton {
                background-color: #222834;
                color: #E2E8F0;
                border: 1px solid #3B465A;
                border-radius: 8px;
                padding: 6px 14px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #334155;
                border-color: #64748B;
            }
            QPushButton:disabled {
                background-color: #1F242E;
                color: #4B5563;
                border-color: #2D3748;
            }
        """)
        self.btn_load.clicked.connect(self.load_requested.emit)
        layout.addWidget(self.btn_load)

        layout.addStretch(1)

        # 3. Status Badge
        self.status_badge = QLabel("● CHƯA NẠP VỤ ÁN", self)
        self.status_badge.setStyleSheet("""
            background-color: #222938;
            color: #38BDF8;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 4px 12px;
            font-size: 11px;
            font-weight: bold;
            letter-spacing: 0.5px;
        """)
        layout.addWidget(self.status_badge)

    def _populate_levels(self) -> None:
        puzzles_dir = Path(__file__).resolve().parent.parent.parent / "puzzles"
        if not puzzles_dir.is_dir():
            return

        entries: list[tuple[int, int, str, str]] = []
        for path in sorted(puzzles_dir.glob("**/*.json")):
            try:
                with open(path, "r", encoding="utf-8") as puzzle_file:
                    data = json.load(puzzle_file)
            except Exception:
                continue

            if data.get("allow_inconsistent", False):
                continue

            size = int(data.get("size", 3))
            puzzle_id = str(data.get("id", path.stem))
            rel_path = path.relative_to(puzzles_dir).as_posix()
            is_tutorial = 0 if "tutorial" in puzzle_id.lower() or "tutorial" in path.stem.lower() else 1
            is_edge = 1 if "edge" in puzzle_id.lower() or "edge" in path.stem.lower() else 0
            prefix = "⚠️ [EDGE]" if is_edge else ("⭐" if is_tutorial == 0 else "🧩")
            label = f"{prefix} [{size}x{size}] {puzzle_id}"
            entries.append((is_tutorial, is_edge * 10 + size, label, rel_path))

        entries.sort(key=lambda item: (item[0], item[1], item[3]))
        for _, _, label, rel_path in entries:
            self.level_combo.addItem(label, rel_path)

    def set_controls_enabled(self, enabled: bool) -> None:
        self.level_combo.setEnabled(enabled)
        self.btn_load.setEnabled(enabled)

    def _on_combo_changed(self, index: int) -> None:
        path = self.level_combo.itemData(index)
        if path:
            self.level_selected.emit(path)

    def set_status_text(self, text: str) -> None:
        self.status_badge.setText(text)


class ClueBanner(QFrame):
    """Dải băng hiển thị manh mối và thông tin suy luận trọng tâm bên dưới bàn cờ."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(72)
        self.setStyleSheet("""
            QFrame {
                background-color: #191E28;
                border: 1.5px solid #2B3545;
                border-radius: 12px;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(18, 10, 18, 10)
        layout.setSpacing(14)

        self.icon_badge = QLabel("🔍", self)
        self.icon_badge.setStyleSheet("font-size: 22px; background: transparent; border: none;")
        layout.addWidget(self.icon_badge)

        text_layout = QVBoxLayout()
        text_layout.setSpacing(2)

        self.title_label = QLabel("MANH MỐI ĐIỀU TRA", self)
        self.title_label.setStyleSheet("color: #F59E0B; font-family: 'Segoe UI'; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        text_layout.addWidget(self.title_label)

        self.clue_label = QLabel("Nhấp vào một thẻ nhân vật đã giải để xem lời khai và tô sáng các đối tượng liên quan.", self)
        self.clue_label.setWordWrap(True)
        self.clue_label.setStyleSheet("color: #F1F5F9; font-family: 'Georgia'; font-size: 13px; font-style: italic; background: transparent; border: none;")
        text_layout.addWidget(self.clue_label)

        layout.addLayout(text_layout, stretch=1)

    def display_clue(self, clue: Clue | None, char_name: str = "", char_job: str = "") -> None:
        if clue is None:
            self.title_label.setText("MANH MỐI ĐIỀU TRA")
            self.title_label.setStyleSheet("color: #64748B; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
            self.clue_label.setText("Nhấp vào một thẻ nhân vật đã giải để xem lời khai và tô sáng các đối tượng liên quan.")
            return

        owner_text = f"LỜI KHAI CỦA [{clue.owner}] {char_name.upper()} ({char_job.upper()})"
        self.title_label.setText(owner_text)
        self.title_label.setStyleSheet("color: #F59E0B; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        desc = format_clue_description(clue)
        self.clue_label.setText(f"“{desc.split('] ', 1)[-1]}”")

    def display_message(self, title: str, message: str, is_warning: bool = False) -> None:
        color = "#EF4444" if is_warning else "#38BDF8"
        self.title_label.setText(title.upper())
        self.title_label.setStyleSheet(f"color: {color}; font-size: 11px; font-weight: bold; letter-spacing: 1px; background: transparent; border: none;")
        self.clue_label.setText(message)


class BottomBar(QWidget):
    """Thanh điều khiển dưới cùng: Ghi chú, Gợi ý, Tự động giải, Tốc độ, Chơi lại."""

    restart_requested = pyqtSignal()
    hint_requested = pyqtSignal()
    auto_solve_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    speed_changed = pyqtSignal(int)
    mark_toggled = pyqtSignal(bool)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedHeight(58)
        self._auto_running = False
        self._game_active = False

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 0, 16, 0)
        layout.setSpacing(12)

        # 1. Nút Ghi chú (Mark)
        self.btn_mark = QPushButton("🏷  GHI CHÚ", self)
        self.btn_mark.setCheckable(True)
        self.btn_mark.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_mark.setStyleSheet(self._btn_style("#334155", "#64748B"))
        self.btn_mark.toggled.connect(self.mark_toggled.emit)
        layout.addWidget(self.btn_mark)

        # 2. Nút Gợi ý (Hint)
        self.btn_hint = QPushButton("💡  GỢI Ý", self)
        self.btn_hint.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_hint.setStyleSheet(self._btn_style("#0369A1", "#0284C7"))
        self.btn_hint.clicked.connect(self.hint_requested.emit)
        layout.addWidget(self.btn_hint)

        # 3. Nút Tự động giải (Auto Solve)
        self.btn_auto_solve = QPushButton("⚡  TỰ ĐỘNG GIẢI", self)
        self.btn_auto_solve.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_auto_solve.setStyleSheet(self._btn_style("#6D28D9", "#7C3AED"))
        self.btn_auto_solve.clicked.connect(self._on_auto_clicked)
        layout.addWidget(self.btn_auto_solve)

        # 4. Thanh trượt tốc độ giải
        speed_box = QHBoxLayout()
        speed_box.setSpacing(8)
        speed_lbl = QLabel("Tốc độ:", self)
        speed_lbl.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: 600;")
        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.setRange(MIN_STEP_DELAY_MS, MAX_STEP_DELAY_MS)
        self.speed_slider.setSingleStep(100)
        self.speed_slider.setValue(MAX_STEP_DELAY_MS + MIN_STEP_DELAY_MS - DEFAULT_STEP_DELAY_MS)
        self.speed_slider.setFixedWidth(120)
        self.speed_slider.valueChanged.connect(self._on_slider_changed)

        self.speed_val_lbl = QLabel(f"{DEFAULT_STEP_DELAY_MS}ms", self)
        self.speed_val_lbl.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: bold; min-width: 45px;")
        speed_box.addWidget(speed_lbl)
        speed_box.addWidget(self.speed_slider)
        speed_box.addWidget(self.speed_val_lbl)
        layout.addLayout(speed_box)

        layout.addStretch(1)

        # 5. Nút Chơi lại (Restart)
        self.btn_restart = QPushButton("🔄  CHƠI LẠI", self)
        self.btn_restart.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_restart.setStyleSheet(self._btn_style("#374151", "#4B5563"))
        self.btn_restart.clicked.connect(self.restart_requested.emit)
        layout.addWidget(self.btn_restart)

        # Khởi đầu disable các nút phụ thuộc
        self.set_game_active(False)

    @staticmethod
    def _btn_style(bg: str, hover: str) -> str:
        return f"""
            QPushButton {{
                background-color: {bg};
                color: #FFFFFF;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px;
                padding: 8px 16px;
                font-family: 'Segoe UI';
                font-size: 12px;
                font-weight: bold;
                letter-spacing: 0.5px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: #1F242E;
                color: #4B5563;
                border-color: #2D3748;
            }}
            QPushButton:checked {{
                background-color: #D97706;
                border-color: #F59E0B;
            }}
        """

    @property
    def step_delay_ms(self) -> int:
        return MAX_STEP_DELAY_MS + MIN_STEP_DELAY_MS - self.speed_slider.value()

    @property
    def is_auto_running(self) -> bool:
        return self._auto_running

    def set_game_active(self, active: bool) -> None:
        self._game_active = active
        if not self._auto_running:
            self.btn_mark.setEnabled(active)
            self.btn_hint.setEnabled(active)
            self.btn_auto_solve.setEnabled(active)
            self.btn_restart.setEnabled(active)

    def set_auto_running(self, running: bool) -> None:
        self._auto_running = running
        self.btn_auto_solve.setText("⏹  DỪNG" if running else "⚡  TỰ ĐỘNG GIẢI")
        self.btn_auto_solve.setStyleSheet(
            self._btn_style("#B91C1C", "#DC2626") if running else self._btn_style("#6D28D9", "#7C3AED")
        )
        self.btn_mark.setEnabled(not running)
        self.btn_hint.setEnabled(self._game_active and not running)
        self.btn_restart.setEnabled(self._game_active and not running)

    def _on_auto_clicked(self) -> None:
        if self._auto_running:
            self.stop_requested.emit()
        else:
            self.auto_solve_requested.emit()

    def _on_slider_changed(self, _val: int) -> None:
        delay = self.step_delay_ms
        self.speed_val_lbl.setText(f"{delay}ms")
        self.speed_changed.emit(delay)


class ControlPanel(QWidget):
    """Facade tổng hợp tương thích với app.py cũ nếu có gọi."""

    load_requested = pyqtSignal()
    level_selected = pyqtSignal(str)
    restart_requested = pyqtSignal()
    hint_requested = pyqtSignal()
    auto_solve_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    speed_changed = pyqtSignal(int)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.header = HeaderBar(self)
        self.bottom = BottomBar(self)

        # Chuyển tiếp tín hiệu
        self.header.load_requested.connect(self.load_requested.emit)
        self.header.level_selected.connect(self.level_selected.emit)
        self.bottom.restart_requested.connect(self.restart_requested.emit)
        self.bottom.hint_requested.connect(self.hint_requested.emit)
        self.bottom.auto_solve_requested.connect(self.auto_solve_requested.emit)
        self.bottom.stop_requested.connect(self.stop_requested.emit)
        self.bottom.speed_changed.connect(self.speed_changed.emit)

    @property
    def step_delay_ms(self) -> int:
        return self.bottom.step_delay_ms

    @property
    def is_auto_running(self) -> bool:
        return self.bottom.is_auto_running

    def set_game_active(self, active: bool) -> None:
        self.bottom.set_game_active(active)

    def set_auto_running(self, running: bool) -> None:
        self.bottom.set_auto_running(running)
        self.header.set_controls_enabled(not running)
