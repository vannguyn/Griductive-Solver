"""Control panel widget hosting action buttons and solver controls.

Tác dụng:
    Thanh điều khiển trò chơi chứa các nút bấm hành động:
    - Nút Load: yêu cầu mở QFileDialog (mặc định thư mục Source/puzzles/) để chọn file puzzle.
    - Nút Restart: Khôi phục bàn chơi về KB_0.
    - Nút Hint: Yêu cầu gợi ý từ tác tử logic.
    - Nút Auto Solve: Chạy tự động giải từng bước; khi đang chạy nút chuyển thành "Dừng".
    - Slider tốc độ: điều chỉnh khoảng thời gian giữa hai bước Auto Solve.

Input:
    Thao tác nhấn nút của người dùng.

Output:
    Các tín hiệu Qt: load_requested, restart_requested, hint_requested,
    auto_solve_requested, stop_requested, speed_changed(int ms).

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

MIN_STEP_DELAY_MS = 100
MAX_STEP_DELAY_MS = 2000
DEFAULT_STEP_DELAY_MS = 600


class ControlPanel(QWidget):
    """Panel chứa các nút điều khiển chính của trò chơi."""

    load_requested = pyqtSignal()
    restart_requested = pyqtSignal()
    hint_requested = pyqtSignal()
    auto_solve_requested = pyqtSignal()
    stop_requested = pyqtSignal()
    speed_changed = pyqtSignal(int)  # độ trễ giữa hai bước (ms)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._auto_running = False
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

        speed_layout = QHBoxLayout()
        self.speed_title = QLabel("Tốc độ giải tự động:", self)
        self.speed_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.speed_slider.setRange(MIN_STEP_DELAY_MS, MAX_STEP_DELAY_MS)
        self.speed_slider.setSingleStep(100)
        # Kéo sang phải = nhanh hơn: giá trị slider là (MAX + MIN - delay).
        self.speed_slider.setValue(self._delay_to_slider(DEFAULT_STEP_DELAY_MS))
        self.speed_label = QLabel(f"{DEFAULT_STEP_DELAY_MS} ms/bước", self)
        speed_layout.addWidget(self.speed_title)
        speed_layout.addWidget(self.speed_slider, stretch=1)
        speed_layout.addWidget(self.speed_label)
        self.main_layout.addLayout(speed_layout)

        # Kết nối sự kiện
        self.btn_load.clicked.connect(self.load_requested.emit)
        self.btn_restart.clicked.connect(self.restart_requested.emit)
        self.btn_hint.clicked.connect(self.hint_requested.emit)
        self.btn_auto_solve.clicked.connect(self._on_auto_clicked)
        self.speed_slider.valueChanged.connect(self._on_slider_changed)

    @staticmethod
    def _delay_to_slider(delay_ms: int) -> int:
        return MAX_STEP_DELAY_MS + MIN_STEP_DELAY_MS - delay_ms

    @property
    def step_delay_ms(self) -> int:
        """Độ trễ hiện tại giữa hai bước Auto Solve (ms)."""
        return self._delay_to_slider(self.speed_slider.value())

    @property
    def is_auto_running(self) -> bool:
        """True nếu giao diện đang ở chế độ Auto Solve."""
        return self._auto_running

    def set_auto_running(self, running: bool) -> None:
        """Chuyển giao diện giữa chế độ chơi tay và chế độ Auto Solve.

        Khi đang chạy: nút Auto Solve thành "Dừng", khóa Load/Restart/Hint
        để tránh thao tác chồng lên generator đang chạy.
        """
        self._auto_running = running
        self.btn_auto_solve.setText("⏹ Dừng" if running else "⚡ Tự động giải")
        self.btn_load.setEnabled(not running)
        self.btn_restart.setEnabled(not running)
        self.btn_hint.setEnabled(not running)

    def _on_auto_clicked(self) -> None:
        if self._auto_running:
            self.stop_requested.emit()
        else:
            self.auto_solve_requested.emit()

    def _on_slider_changed(self, _value: int) -> None:
        delay = self.step_delay_ms
        self.speed_label.setText(f"{delay} ms/bước")
        self.speed_changed.emit(delay)
