"""Control panel widget hosting action buttons and solver controls.

Tác dụng:
    Thanh điều khiển trò chơi chứa các nút bấm hành động:
    - Nút Load: Mở QFileDialog (mặc định thư mục Source/puzzles/) để chọn file puzzle.
    - Nút Restart: Khôi phục bàn chơi về KB_0.
    - Nút Hint: Yêu cầu gợi ý từ tác tử logic.
    - Nút Auto Solve: Chạy tự động giải từng bước (kèm Slider điều chỉnh tốc độ).

Input:
    Thao tác nhấn nút của người dùng.

Output:
    Các tín hiệu Qt (load_clicked, restart_clicked, hint_clicked, auto_solve_clicked).

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)


class ControlPanel(QWidget):
    """Panel chứa các nút điều khiển chính của trò chơi."""

    load_requested = pyqtSignal()
    restart_requested = pyqtSignal()
    hint_requested = pyqtSignal()
    auto_solve_requested = pyqtSignal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.main_layout = QVBoxLayout(self)
        btn_layout = QHBoxLayout()

        self.btn_load = QPushButton("📁 Tải Puzzle", self)
        self.btn_restart = QPushButton("🔄 Chơi lại", self)
        self.btn_hint = QPushButton("💡 Gợi ý", self)
        self.btn_auto_solve = QPushButton("⚡ Tự động giải", self)

        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_restart)
        btn_layout.addWidget(self.btn_hint)
        btn_layout.addWidget(self.btn_auto_solve)

        self.main_layout.addLayout(btn_layout)

        # Kết nối sự kiện
        self.btn_load.clicked.connect(self.load_requested.emit)
        self.btn_restart.clicked.connect(self.restart_requested.emit)
        self.btn_hint.clicked.connect(self.hint_requested.emit)
        self.btn_auto_solve.clicked.connect(self.auto_solve_requested.emit)
