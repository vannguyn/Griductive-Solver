"""Procedural avatar renderer for Grid Detective characters.

Tác dụng:
    Vẽ avatar hình minh họa chân dung độc bản cho 25 nhân vật (Ada..Yuri)
    theo phong cách cozy detective / editorial illustration bằng QPainter.
    Tự động chống răng cưa (anti-aliasing), độ phân giải sắc nét, màu sắc muted sang trọng.
"""

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QGuiApplication, QPainter, QPainterPath, QPen, QPixmap

_AVATAR_CACHE: dict[tuple[str, int, float, int], QPixmap] = {}
_MAX_AVATAR_CACHE_ENTRIES = 256

# Bảng phối màu palette editorial ấm cúng
PALETTE = {
    "bg_circle": QColor("#222733"),
    "skin_fair": QColor("#F8D7C4"),
    "skin_warm": QColor("#E8BA9B"),
    "skin_tan": QColor("#C68B59"),
    "hair_dark": QColor("#2C221E"),
    "hair_brown": QColor("#4E3629"),
    "hair_blonde": QColor("#D4A359"),
    "hair_auburn": QColor("#8D3B2B"),
    "hair_gray": QColor("#7A7D84"),
    "cloth_navy": QColor("#2B3A4A"),
    "cloth_cream": QColor("#E2DAC6"),
    "cloth_maroon": QColor("#702632"),
    "cloth_forest": QColor("#244230"),
    "cloth_mustard": QColor("#C28834"),
    "cloth_slate": QColor("#4B5563"),
}

# Thông tin tạo hình của từng nhân vật
CHARACTER_PROFILES = {
    "Ada": {"skin": "skin_fair", "hair": "hair_dark", "cloth": "cloth_cream", "glasses": True, "style": "bun"},
    "Ben": {"skin": "skin_warm", "hair": "hair_brown", "cloth": "cloth_navy", "cap": True, "style": "short"},
    "Cara": {"skin": "skin_tan", "hair": "hair_auburn", "cloth": "cloth_mustard", "hat": True, "style": "braid"},
    "Dev": {"skin": "skin_fair", "hair": "hair_brown", "cloth": "cloth_slate", "goggles": True, "style": "windswept"},
    "Elle": {"skin": "skin_warm", "hair": "hair_dark", "cloth": "cloth_cream", "chef_hat": True, "style": "tied"},
    "Finn": {"skin": "skin_fair", "hair": "hair_blonde", "cloth": "cloth_navy", "stethoscope": True, "style": "parted"},
    "Gwen": {"skin": "skin_fair", "hair": "hair_auburn", "cloth": "cloth_maroon", "beret": True, "style": "wavy"},
    "Hugo": {"skin": "skin_tan", "hair": "hair_dark", "cloth": "cloth_mustard", "hardhat": True, "style": "short"},
    "Isla": {"skin": "skin_warm", "hair": "hair_blonde", "cloth": "cloth_forest", "flower": True, "style": "long"},
    "Jams": {"skin": "skin_warm", "hair": "hair_dark", "cloth": "cloth_navy", "fedora": True, "style": "short"},
    "Kino": {"skin": "skin_fair", "hair": "hair_dark", "cloth": "cloth_slate", "headphones": True, "style": "short"},
    "Luke": {"skin": "skin_tan", "hair": "hair_brown", "cloth": "cloth_navy", "safety_glasses": True, "style": "short"},
    "Mara": {"skin": "skin_warm", "hair": "hair_auburn", "cloth": "cloth_cream", "badge": True, "style": "bob"},
    "Nuby": {"skin": "skin_fair", "hair": "hair_gray", "cloth": "cloth_navy", "tie": True, "style": "receding"},
    "Owen": {"skin": "skin_warm", "hair": "hair_brown", "cloth": "cloth_slate", "glasses": True, "style": "parted"},
    "Piper": {"skin": "skin_fair", "hair": "hair_dark", "cloth": "cloth_cream", "lab_goggles": True, "style": "ponytail"},
    "Quinn": {"skin": "skin_tan", "hair": "hair_dark", "cloth": "cloth_maroon", "stylish_glasses": True, "style": "undercut"},
    "Ruby": {"skin": "skin_fair", "hair": "hair_auburn", "cloth": "cloth_forest", "beanie": True, "style": "shoulder"},
    "Sam": {"skin": "skin_warm", "hair": "hair_dark", "cloth": "cloth_navy", "bandana": True, "style": "crew"},
    "Tony": {"skin": "skin_tan", "hair": "hair_brown", "cloth": "cloth_slate", "earpiece": True, "style": "short"},
    "Uma": {"skin": "skin_warm", "hair": "hair_gray", "cloth": "cloth_cream", "scarf": True, "style": "updo"},
    "Victor": {"skin": "skin_fair", "hair": "hair_dark", "cloth": "cloth_navy", "chauffeur": True, "style": "short"},
    "Will": {"skin": "skin_warm", "hair": "hair_blonde", "cloth": "cloth_navy", "officer_badge": True, "style": "side_part"},
    "Xena": {"skin": "skin_fair", "hair": "hair_brown", "cloth": "cloth_maroon", "spectacles": True, "style": "bun"},
    "Yuri": {"skin": "skin_warm", "hair": "hair_dark", "cloth": "cloth_navy", "star_pin": True, "style": "curly"},
}


def get_character_avatar(name: str, size: int = 80, dpr: float = 1.0) -> QPixmap:
    """Tạo QPixmap vẽ chân dung độc bản của nhân vật theo kích thước mong muốn (có cache)."""
    dpr_norm = max(1.0, round(float(dpr), 2))
    app = QGuiApplication.instance()
    app_id = id(app) if app is not None else 0
    cache_key = (name, size, dpr_norm, app_id)
    cached = _AVATAR_CACHE.get(cache_key)
    if cached is not None:
        return cached

    px_size = max(1, round(size * dpr_norm))
    pixmap = QPixmap(px_size, px_size)
    pixmap.setDevicePixelRatio(dpr_norm)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    prof = CHARACTER_PROFILES.get(name, {
        "skin": "skin_warm", "hair": "hair_dark", "cloth": "cloth_navy", "style": "short"
    })

    skin_color = PALETTE[prof.get("skin", "skin_warm")]
    hair_color = PALETTE[prof.get("hair", "hair_dark")]
    cloth_color = PALETTE[prof.get("cloth", "cloth_navy")]

    # 1. Nền hình tròn khung tranh
    center = size / 2.0
    radius = size * 0.46
    painter.setBrush(QBrush(PALETTE["bg_circle"]))
    painter.setPen(QPen(QColor("#3E4656"), max(1.5, size * 0.03)))
    painter.drawEllipse(QPointF(center, center), radius, radius)

    # Vùng clip hình tròn để vai/áo không tràn ra ngoài
    clip_path = QPainterPath()
    clip_path.addEllipse(QPointF(center, center), radius - 1, radius - 1)
    painter.setClipPath(clip_path)

    # 2. Vẽ vai áo (Clothing / Torso)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(cloth_color))
    torso_rect = QRectF(size * 0.15, size * 0.70, size * 0.70, size * 0.40)
    painter.drawChord(torso_rect, 0, 180 * 16)

    # Cổ áo
    painter.setBrush(QBrush(skin_color.darker(110)))
    neck_rect = QRectF(size * 0.42, size * 0.58, size * 0.16, size * 0.18)
    painter.drawRect(neck_rect)

    # 3. Vẽ khuôn mặt (Head / Face)
    painter.setBrush(QBrush(skin_color))
    face_rect = QRectF(size * 0.30, size * 0.28, size * 0.40, size * 0.42)
    painter.drawRoundedRect(face_rect, size * 0.18, size * 0.18)

    # 4. Tóc (Hair style)
    painter.setBrush(QBrush(hair_color))
    style = prof.get("style", "short")
    if style in ("bun", "updo"):
        # Búi tóc trên đỉnh
        painter.drawEllipse(QPointF(center, size * 0.24), size * 0.15, size * 0.12)
        painter.drawRoundedRect(QRectF(size * 0.28, size * 0.24, size * 0.44, size * 0.18), size * 0.1, size * 0.1)
    elif style == "long" or style == "wavy":
        # Tóc dài hai bên
        painter.drawRoundedRect(QRectF(size * 0.24, size * 0.24, size * 0.52, size * 0.38), size * 0.12, size * 0.12)
    else:
        # Tóc ngắn tiêu chuẩn
        painter.drawRoundedRect(QRectF(size * 0.27, size * 0.24, size * 0.46, size * 0.18), size * 0.08, size * 0.08)

    # 5. Chi tiết mắt (Eyes)
    painter.setBrush(QBrush(QColor("#1E222B")))
    eye_y = size * 0.45
    eye_r = max(1.5, size * 0.025)
    painter.drawEllipse(QPointF(size * 0.40, eye_y), eye_r, eye_r)
    painter.drawEllipse(QPointF(size * 0.60, eye_y), eye_r, eye_r)

    # 6. Mũ / Kính / Phụ kiện đặc trưng nghề nghiệp
    if prof.get("glasses") or prof.get("spectacles") or prof.get("stylish_glasses"):
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(QColor("#D6A75C"), max(1.2, size * 0.025)))
        painter.drawEllipse(QPointF(size * 0.40, eye_y), size * 0.065, size * 0.065)
        painter.drawEllipse(QPointF(size * 0.60, eye_y), size * 0.065, size * 0.065)
        painter.drawLine(QPointF(size * 0.465, eye_y), QPointF(size * 0.535, eye_y))

    if prof.get("fedora") or prof.get("hat"):
        painter.setBrush(QBrush(QColor("#453326")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(size * 0.20, size * 0.26, size * 0.60, size * 0.05))
        painter.drawRoundedRect(QRectF(size * 0.30, size * 0.16, size * 0.40, size * 0.14), size * 0.04, size * 0.04)

    if prof.get("beret"):
        painter.setBrush(QBrush(PALETTE["cloth_maroon"]))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center + size * 0.04, size * 0.22), size * 0.22, size * 0.09)

    if prof.get("chef_hat"):
        painter.setBrush(QBrush(QColor("#FFFFFF")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(center, size * 0.18), size * 0.18, size * 0.12)
        painter.drawRect(QRectF(size * 0.32, size * 0.22, size * 0.36, size * 0.08))

    if prof.get("hardhat"):
        painter.setBrush(QBrush(QColor("#F59E0B")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(QRectF(size * 0.26, size * 0.18, size * 0.48, size * 0.14), size * 0.06, size * 0.06)

    painter.end()
    if app is not None:
        if len(_AVATAR_CACHE) >= _MAX_AVATAR_CACHE_ENTRIES:
            _AVATAR_CACHE.clear()
        _AVATAR_CACHE[cache_key] = pixmap
    return pixmap
