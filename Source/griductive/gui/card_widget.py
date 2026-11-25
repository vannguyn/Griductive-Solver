"""Custom tactile Character Card Widget for Grid Detective.

Tác dụng:
    Thành phần thẻ nhân vật tương tác chính:
    - Hiển thị chân dung minh họa avatar (procedural vector), tên nhân vật, nghề nghiệp, tọa độ.
    - Hỗ trợ các trạng thái: Chưa mở (Unknown), Vô tội (Innocent), Tội phạm (Criminal).
    - Hỗ trợ highlight phân tầng (Subject, Target, Hint) và làm mờ (Dimmed).
    - Hiệu ứng lật thẻ 3D (Flip animation) mượt mà (~360ms).
    - Hiệu ứng rung lắc (Shake animation) cảnh báo phản hồi khi người chơi phán đoán sai hoặc chưa đủ chứng cứ.
"""

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, QSize, Qt, QVariantAnimation, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPen
from PyQt6.QtWidgets import QWidget
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicCell
from griductive.domain.types import Status
from griductive.gui.assets.avatars import get_character_avatar

# Kích thước thẻ tiêu chuẩn
CARD_BASE_WIDTH = 135
CARD_BASE_HEIGHT = 165
FLIP_HALF_MS = 175
SHAKE_MS = 320

# Màu sắc thẻ editorial
COLOR_UNKNOWN_BG = QColor("#222834")
COLOR_UNKNOWN_BORDER = QColor("#364052")
COLOR_UNKNOWN_TEXT = QColor("#E2E8F0")

COLOR_INNOCENT_BG = QColor("#183024")
COLOR_INNOCENT_BORDER = QColor("#285A3F")
COLOR_INNOCENT_BADGE = QColor("#22C55E")
COLOR_INNOCENT_TEXT = QColor("#DCFCE7")

COLOR_CRIMINAL_BG = QColor("#3A1C22")
COLOR_CRIMINAL_BORDER = QColor("#6B2936")
COLOR_CRIMINAL_BADGE = QColor("#EF4444")
COLOR_CRIMINAL_TEXT = QColor("#FEE2E2")

COLOR_HIGHLIGHT_SUBJECT = QColor("#F59E0B")  # Vàng hổ phách cho chủ thể clue
COLOR_HIGHLIGHT_TARGET = QColor("#10B981")   # Xanh ngọc lục bảo cho đối tượng liên quan
COLOR_HIGHLIGHT_HINT = QColor("#38BDF8")     # Xanh da trời cho ô gợi ý


class CharacterCardWidget(QWidget):
    """Widget thẻ nhân vật tương tác hiển thị trên bàn cờ Grid Detective."""

    card_clicked = pyqtSignal(str)        # coord
    card_right_clicked = pyqtSignal(str)  # coord

    def __init__(self, coord: Coord, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.coord = coord
        self.char_name = ""
        self.char_job = ""
        self.revealed = False
        self.status: Status | None = None

        # Trạng thái hiển thị nâng cao
        self.highlight_role: str | None = None  # "subject" | "target" | "hint" | None
        self.is_dimmed = False
        self.is_hovered = False

        # Quản lý hoạt ảnh
        self._scale_x = 1.0
        self._shake_offset = 0.0
        self._flip_anim: QVariantAnimation | None = None
        self._shake_anim: QVariantAnimation | None = None

        self.setMinimumSize(CARD_BASE_WIDTH, CARD_BASE_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        return QSize(CARD_BASE_WIDTH, CARD_BASE_HEIGHT)

    def set_cell_data(self, cell: PublicCell, animate_flip_if_new: bool = False) -> None:
        """Cập nhật dữ liệu từ PublicCell, kích hoạt flip nếu thẻ vừa được mở."""
        old_revealed = self.revealed
        self.char_name = cell.name
        self.char_job = cell.job
        self.status = cell.status
        new_revealed = cell.revealed

        if animate_flip_if_new and not old_revealed and new_revealed:
            self.revealed = old_revealed  # Giữ trạng thái cũ cho nửa đầu animation
            self._start_flip_animation(target_revealed=new_revealed)
        else:
            self.revealed = new_revealed
            self.update()

    def set_spotlight(self, role: str | None, dimmed: bool = False) -> None:
        """Cập nhật trạng thái tô sáng hoặc làm mờ theo ngữ cảnh clue."""
        if self.highlight_role != role or self.is_dimmed != dimmed:
            self.highlight_role = role
            self.is_dimmed = dimmed
            self.update()

    def shake(self) -> None:
        """Kích hoạt hiệu ứng rung lắc nhẹ khi phán đoán bị từ chối."""
        if self._shake_anim is not None and self._shake_anim.state() == QVariantAnimation.State.Running:
            self._shake_anim.stop()

        anim = QVariantAnimation(self)
        anim.setDuration(SHAKE_MS)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.InOutSine)

        def on_shake_step(t: object) -> None:
            # Sóng dao động giảm dần: -8, +8, -5, +5, -2, 0
            val = float(t)
            import math
            decay = 1.0 - val
            offset = 9.0 * math.sin(val * math.pi * 5.0) * decay
            self._shake_offset = offset
            self.update()

        def on_shake_done() -> None:
            self._shake_offset = 0.0
            self.update()

        anim.valueChanged.connect(on_shake_step)
        anim.finished.connect(on_shake_done)
        self._shake_anim = anim
        anim.start()

    def _start_flip_animation(self, target_revealed: bool) -> None:
        """Hoạt ảnh lật thẻ 3D: co hẹp theo trục X rồi nở ra với mặt mới."""
        if self._flip_anim is not None and self._flip_anim.state() == QVariantAnimation.State.Running:
            self._flip_anim.stop()

        anim1 = QVariantAnimation(self)
        anim1.setDuration(FLIP_HALF_MS)
        anim1.setStartValue(1.0)
        anim1.setEndValue(0.0)
        anim1.setEasingCurve(QEasingCurve.Type.InCubic)

        def on_shrink(val: object) -> None:
            self._scale_x = float(val)
            self.update()

        def on_halfway() -> None:
            # Đổi mặt thẻ
            self.revealed = target_revealed
            anim2 = QVariantAnimation(self)
            anim2.setDuration(FLIP_HALF_MS)
            anim2.setStartValue(0.0)
            anim2.setEndValue(1.0)
            anim2.setEasingCurve(QEasingCurve.Type.OutCubic)

            def on_grow(val: object) -> None:
                self._scale_x = float(val)
                self.update()

            def on_done() -> None:
                self._scale_x = 1.0
                self.update()

            anim2.valueChanged.connect(on_grow)
            anim2.finished.connect(on_done)
            self._flip_anim = anim2
            anim2.start()

        anim1.valueChanged.connect(on_shrink)
        anim1.finished.connect(on_halfway)
        self._flip_anim = anim1
        anim1.start()

    # ------------------------------------------------------------- Events
    def enterEvent(self, event: object) -> None:
        self.is_hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event: object) -> None:
        self.is_hovered = False
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.card_clicked.emit(self.coord)
        elif event.button() == Qt.MouseButton.RightButton:
            self.card_right_clicked.emit(self.coord)
        super().mousePressEvent(event)

    # ----------------------------------------------------------- Painting
    def paintEvent(self, event: object) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        width = float(self.width())
        height = float(self.height())

        # Độ mờ khi thẻ không thuộc spotlight
        opacity = 0.35 if self.is_dimmed else 1.0
        painter.setOpacity(opacity)

        # Áp dụng rung lắc và tỷ lệ lật X
        center_x = width / 2.0 + self._shake_offset
        center_y = height / 2.0

        painter.translate(center_x, center_y)
        painter.scale(self._scale_x, 1.0)
        painter.translate(-width / 2.0, -height / 2.0)

        # 1. Xác định màu nền và viền
        if not self.revealed:
            bg_color = COLOR_UNKNOWN_BG
            border_color = COLOR_UNKNOWN_BORDER
            text_color = COLOR_UNKNOWN_TEXT
        elif self.status == Status.CRIMINAL:
            bg_color = COLOR_CRIMINAL_BG
            border_color = COLOR_CRIMINAL_BORDER
            text_color = COLOR_CRIMINAL_TEXT
        else:
            bg_color = COLOR_INNOCENT_BG
            border_color = COLOR_INNOCENT_BORDER
            text_color = COLOR_INNOCENT_TEXT

        # Xử lý viền nổi bật (Highlight)
        border_width = 1.5
        if self.highlight_role == "subject":
            border_color = COLOR_HIGHLIGHT_SUBJECT
            border_width = 3.5
        elif self.highlight_role == "target":
            border_color = COLOR_HIGHLIGHT_TARGET
            border_width = 3.5
        elif self.highlight_role == "hint":
            border_color = COLOR_HIGHLIGHT_HINT
            border_width = 4.0
        elif self.is_hovered:
            border_color = border_color.lighter(135)
            border_width = 2.5

        # 2. Vẽ hình thân thẻ với góc bo tròn sang trọng
        card_rect = QRectF(2.0, 2.0, width - 4.0, height - 4.0)
        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, border_width))
        painter.drawRoundedRect(card_rect, 12.0, 12.0)

        # 3. Vẽ nhãn tọa độ góc trên bên trái [A1]
        painter.setPen(QPen(border_color.lighter(130)))
        coord_font = QFont("Segoe UI", 9, QFont.Weight.Bold)
        painter.setFont(coord_font)
        painter.drawText(QRectF(10.0, 8.0, 40.0, 20.0), int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), self.coord)

        # 4. Vẽ Avatar chân dung minh họa ở trung tâm
        avatar_size = int(min(width * 0.44, height * 0.36))
        avatar_x = int((width - avatar_size) / 2.0)
        avatar_y = int(height * 0.16)
        pix = get_character_avatar(self.char_name, avatar_size)
        painter.drawPixmap(avatar_x, avatar_y, pix)

        # 5. Vẽ Tên nhân vật (Editorial typography)
        name_font = QFont("Georgia", 11, QFont.Weight.Bold)
        painter.setFont(name_font)
        painter.setPen(QPen(text_color))
        name_rect = QRectF(6.0, height * 0.58, width - 12.0, 22.0)
        painter.drawText(name_rect, int(Qt.AlignmentFlag.AlignCenter), self.char_name.upper())

        # 6. Vẽ Nghề nghiệp (Profession subtitle)
        job_font = QFont("Segoe UI", 8, QFont.Weight.DemiBold)
        job_font.setLetterSpacing(QFont.SpacingType.AbsoluteSpacing, 0.8)
        painter.setFont(job_font)
        painter.setPen(QPen(text_color.darker(125)))
        job_rect = QRectF(6.0, height * 0.72, width - 12.0, 18.0)
        painter.drawText(job_rect, int(Qt.AlignmentFlag.AlignCenter), self.char_job.upper())

        # 7. Vẽ Thanh trạng thái (Badge footer)
        badge_rect = QRectF(12.0, height * 0.84, width - 24.0, 20.0)
        badge_path = QPainterPath()
        badge_path.addRoundedRect(badge_rect, 6.0, 6.0)

        if not self.revealed:
            painter.fillPath(badge_path, QBrush(QColor("#2C3444")))
            painter.setPen(QPen(QColor("#94A3B8")))
            badge_text = "❓ CHƯA RÕ"
        elif self.status == Status.CRIMINAL:
            painter.fillPath(badge_path, QBrush(QColor("#541E28")))
            painter.setPen(QPen(COLOR_CRIMINAL_BADGE))
            badge_text = "🔴 TỘI PHẠM"
        else:
            painter.fillPath(badge_path, QBrush(QColor("#1A402D")))
            painter.setPen(QPen(COLOR_INNOCENT_BADGE))
            badge_text = "🟢 VÔ TỘI"

        badge_font = QFont("Segoe UI", 8, QFont.Weight.Bold)
        painter.setFont(badge_font)
        painter.drawText(badge_rect, int(Qt.AlignmentFlag.AlignCenter), badge_text)
