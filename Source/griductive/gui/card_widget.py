"""Custom tactile Character Card Widget for Grid Detective.

Tác dụng:
    Thành phần thẻ nhân vật tương tác chính:
    - Hiển thị chân dung minh họa avatar (procedural vector), tên nhân vật, nghề nghiệp, tọa độ.
    - Hỗ trợ các trạng thái: Chưa mở (Unknown), Vô tội (Innocent), Tội phạm (Criminal).
    - Hỗ trợ highlight phân tầng (Subject, Target, Hint) và làm mờ (Dimmed).
    - Hiệu ứng lật thẻ 3D (Flip animation) mượt mà (~360ms).
    - Hiệu ứng rung lắc (Shake animation) cảnh báo phản hồi khi người chơi phán đoán sai hoặc chưa đủ chứng cứ.
"""

import math

from PyQt6.QtCore import QEasingCurve, QRectF, QSize, Qt, QVariantAnimation, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QFont, QMouseEvent, QPainter, QPainterPath, QPen, QPixmap
from PyQt6.QtWidgets import QWidget
from griductive.domain.grid import Coord
from griductive.domain.public_state import PublicCell
from griductive.domain.types import Status
from griductive.gui.assets.avatars import get_character_avatar

# Kích thước thẻ tiêu chuẩn
CARD_BASE_WIDTH = 135
CARD_BASE_HEIGHT = 165
FLIP_HALF_MS = 175
FLIP_DURATION_MS = FLIP_HALF_MS * 2
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

        # Quản lý hoạt ảnh & bộ đệm mặt thẻ
        self._display_revealed = False
        self._flip_target_revealed = False
        self._scale_x = 1.0
        self._shake_offset = 0.0
        self._flip_anim: QVariantAnimation | None = None
        self._shake_anim: QVariantAnimation | None = None
        self._face_cache: QPixmap | None = None
        self._face_cache_key: tuple | None = None

        self.setMinimumSize(CARD_BASE_WIDTH, CARD_BASE_HEIGHT)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def sizeHint(self) -> QSize:
        return QSize(CARD_BASE_WIDTH, CARD_BASE_HEIGHT)

    def stop_animations(self) -> None:
        """Dừng mọi hoạt ảnh đang chạy và khôi phục trạng thái hình học mặc định."""
        self._stop_flip_animation(reset_scale=True)
        if self._shake_anim is not None:
            if self._shake_anim.state() == QVariantAnimation.State.Running:
                self._shake_anim.stop()
            self._shake_anim = None
        self._shake_offset = 0.0

    def _stop_flip_animation(self, reset_scale: bool = True) -> None:
        if self._flip_anim is not None:
            anim = self._flip_anim
            self._flip_anim = None
            if anim.state() == QVariantAnimation.State.Running:
                anim.stop()
        if reset_scale:
            self._scale_x = 1.0

    def set_cell_data(self, cell: PublicCell, animate_flip_if_new: bool = False) -> None:
        """Cập nhật dữ liệu từ PublicCell, kích hoạt flip nếu thẻ vừa được mở."""
        old_revealed = self.revealed
        self.char_name = cell.name
        self.char_job = cell.job
        self.status = cell.status
        self.revealed = cell.revealed

        if animate_flip_if_new and not old_revealed and cell.revealed:
            self._display_revealed = old_revealed  # Giữ mặt cũ cho nửa đầu animation
            self._start_flip_animation(target_revealed=cell.revealed)
        elif not animate_flip_if_new or not cell.revealed:
            # Khi rebuild / restart / đồng bộ ép buộc, hủy flip cũ để thẻ không kẹt co ngang
            self._stop_flip_animation(reset_scale=True)
            self._display_revealed = cell.revealed
            self.update()
        else:
            # Nếu thẻ đang lật dở cho chính trạng thái mới này, giữ animation tiếp tục mượt mà
            if self._flip_anim is None:
                self._display_revealed = cell.revealed
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
            decay = 1.0 - val
            self._shake_offset = 9.0 * math.sin(val * math.pi * 5.0) * decay
            self.update()

        def on_shake_done() -> None:
            if self._shake_anim is anim:
                self._shake_anim = None
            self._shake_offset = 0.0
            self.update()

        anim.valueChanged.connect(on_shake_step)
        anim.finished.connect(on_shake_done)
        self._shake_anim = anim
        anim.start()

    def _start_flip_animation(self, target_revealed: bool) -> None:
        """Hoạt ảnh lật thẻ 3D liên tục trên một animation duy nhất (không khựng ở điểm giữa)."""
        self._stop_flip_animation(reset_scale=False)
        self._flip_target_revealed = target_revealed

        anim = QVariantAnimation(self)
        anim.setDuration(FLIP_DURATION_MS)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.Type.Linear)

        def on_flip_step(val: object) -> None:
            progress = float(val)
            if progress >= 0.5 and self._display_revealed != self._flip_target_revealed:
                self._display_revealed = self._flip_target_revealed
            # Phép chiếu góc quay 3D: cos(theta) với theta từ 0 -> pi
            self._scale_x = abs(math.cos(progress * math.pi))
            self.update()

        def on_flip_done() -> None:
            if self._flip_anim is anim:
                self._flip_anim = None
            self._display_revealed = self._flip_target_revealed
            self._scale_x = 1.0
            self.update()

        anim.valueChanged.connect(on_flip_step)
        anim.finished.connect(on_flip_done)
        self._flip_anim = anim
        anim.start()

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
    def _get_face_pixmap(self) -> QPixmap:
        """Render mặt thẻ vào QPixmap cache ở tỷ lệ 1.0 để hiệu ứng lật đạt 60fps mượt mà."""
        w = self.width()
        h = self.height()
        dpr = max(1.0, round(float(self.devicePixelRatioF()), 2))
        key = (
            w,
            h,
            dpr,
            self._display_revealed,
            self.status,
            self.highlight_role,
            self.is_hovered,
            self.char_name,
            self.char_job,
            self.coord,
        )
        if self._face_cache is not None and self._face_cache_key == key:
            return self._face_cache

        px_w = max(1, round(w * dpr))
        px_h = max(1, round(h * dpr))
        pixmap = QPixmap(px_w, px_h)
        pixmap.setDevicePixelRatio(dpr)
        pixmap.fill(Qt.GlobalColor.transparent)

        face_painter = QPainter(pixmap)
        face_painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        face_painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self._paint_card_face(face_painter, float(w), float(h), dpr)
        face_painter.end()

        self._face_cache = pixmap
        self._face_cache_key = key
        return pixmap

    def _paint_card_face(self, painter: QPainter, width: float, height: float, dpr: float) -> None:
        """Vẽ toàn bộ nội dung mặt thẻ tại tỷ lệ gốc 1.0."""
        # 1. Xác định màu nền và viền
        if not self._display_revealed:
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
        pix = get_character_avatar(self.char_name, avatar_size, dpr=dpr)
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

        if not self._display_revealed:
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

    def paintEvent(self, event: object) -> None:
        width = float(self.width())
        height = float(self.height())
        if width <= 0.0 or height <= 0.0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # Độ mờ khi thẻ không thuộc spotlight
        opacity = 0.35 if self.is_dimmed else 1.0
        painter.setOpacity(opacity)

        # Áp dụng rung lắc và tỷ lệ lật X (tránh ma trận suy biến 0.0)
        effective_scale_x = max(0.015, self._scale_x)
        center_x = width / 2.0 + self._shake_offset
        center_y = height / 2.0

        painter.translate(center_x, center_y)
        painter.scale(effective_scale_x, 1.0)
        painter.translate(-width / 2.0, -height / 2.0)

        painter.drawPixmap(0, 0, self._get_face_pixmap())
