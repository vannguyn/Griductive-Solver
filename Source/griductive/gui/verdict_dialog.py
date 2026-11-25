"""Editorial modal dialog for player's detective verdict.

Tác dụng:
    Hộp thoại thẩm vấn / nộp phán quyết cho một nghi phạm:
    - Hiển thị chân dung minh họa lớn, tên và nghề nghiệp nhân vật.
    - Cho phép chọn CRIMINAL (Tội phạm) hoặc INNOCENT (Vô tội).
    - Thiết kế theo phong cách hồ sơ trinh thám cozy detective.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPixmap
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from griductive.domain.grid import Coord
from griductive.domain.types import Status
from griductive.gui.assets.avatars import get_character_avatar


class VerdictDialog(QDialog):
    """Hộp thoại quyết định phán quyết điều tra."""

    def __init__(self, coord: Coord, name: str, job: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Hồ sơ điều tra nghi phạm")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        self.setModal(True)
        self.setFixedSize(380, 420)
        self.selected_status: Status | None = None

        self.setStyleSheet("""
            QDialog {
                background-color: #1A1E27;
                border: 2px solid #364052;
                border-radius: 16px;
            }
            QLabel {
                color: #F1F5F9;
            }
            QPushButton {
                font-family: 'Segoe UI';
                font-size: 13px;
                font-weight: bold;
                border-radius: 10px;
                padding: 12px;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 28, 24, 24)
        layout.setSpacing(14)

        # Header tọa độ & hồ sơ
        sub_title = QLabel(f"HỒ SƠ TỌA ĐỘ [{coord}]")
        sub_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_title.setStyleSheet("color: #94A3B8; font-size: 11px; font-weight: bold; letter-spacing: 1.5px;")
        layout.addWidget(sub_title)

        # Avatar minh họa lớn
        avatar_label = QLabel()
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = get_character_avatar(name, 100)
        avatar_label.setPixmap(pix)
        layout.addWidget(avatar_label)

        # Tên & nghề nghiệp
        name_label = QLabel(name.upper())
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #FFFFFF; font-family: 'Georgia'; font-size: 18px; font-weight: bold;")
        layout.addWidget(name_label)

        job_label = QLabel(f"— {job.upper()} —")
        job_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        job_label.setStyleSheet("color: #CBD5E1; font-size: 11px; font-weight: 600; letter-spacing: 1px;")
        layout.addWidget(job_label)

        prompt_label = QLabel("Hãy đưa ra phán quyết logic có thể chứng minh được:")
        prompt_label.setWordWrap(True)
        prompt_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        prompt_label.setStyleSheet("color: #94A3B8; font-size: 11px; margin-top: 6px;")
        layout.addWidget(prompt_label)

        # Các nút bấm lựa chọn
        btn_layout = QVBoxLayout()
        btn_layout.setSpacing(10)

        btn_crim = QPushButton("🔴 CRIMINAL (TỘI PHẠM)")
        btn_crim.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_crim.setStyleSheet("""
            QPushButton {
                background-color: #7F1D1D;
                color: #FEE2E2;
                border: 1.5px solid #DC2626;
            }
            QPushButton:hover {
                background-color: #991B1B;
                border-color: #EF4444;
            }
        """)
        btn_crim.clicked.connect(self._on_criminal)
        btn_layout.addWidget(btn_crim)

        btn_inno = QPushButton("🟢 INNOCENT (VÔ TỘI)")
        btn_inno.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_inno.setStyleSheet("""
            QPushButton {
                background-color: #14532D;
                color: #DCFCE7;
                border: 1.5px solid #16A34A;
            }
            QPushButton:hover {
                background-color: #166534;
                border-color: #22C55E;
            }
        """)
        btn_inno.clicked.connect(self._on_innocent)
        btn_layout.addWidget(btn_inno)

        btn_cancel = QPushButton("HỦY BỎ")
        btn_cancel.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #64748B;
                border: none;
                padding: 6px;
                font-size: 11px;
            }
            QPushButton:hover {
                color: #94A3B8;
            }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def _on_criminal(self) -> None:
        self.selected_status = Status.CRIMINAL
        self.accept()

    def _on_innocent(self) -> None:
        self.selected_status = Status.INNOCENT
        self.accept()
