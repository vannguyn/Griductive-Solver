"""Board view widget rendering the N x N grid and character cards.

Tác dụng:
    Hiển thị giao diện trực quan của lưới bàn cờ N x N:
    - Vẽ các ô cờ với hiệu ứng lật thẻ (card flip).
    - Hiển thị tên nhân vật, nghề nghiệp, và trạng thái (Úp hoặc Ngửa: CRIMINAL / INNOCENT).
    - Hiển thị nhãn tọa độ cột (A, B, ...) và hàng (1, 2, ...).
    - Highlight trực quan các ô cờ liên quan khi người dùng click vào một clue ở CluePanel.
    - Bắt sự kiện click chuột của người dùng để nộp verdict.

Input:
    PublicState từ GameSession.

Output:
    Tín hiệu Qt cell_submitted(coord, Status) khi người chơi chọn CRIMINAL/INNOCENT cho một ô.

Người phụ trách: Gia Hưng (Game Engine, App Session & PyQt6 GUI).
"""

from PyQt6.QtCore import QVariantAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QGridLayout, QLabel, QMenu, QPushButton, QWidget
from griductive.domain.grid import Coord, parse_coord
from griductive.domain.public_state import PublicCell, PublicState
from griductive.domain.types import Status

CARD_MIN_WIDTH = 120
CARD_MIN_HEIGHT = 96
FLIP_HALF_MS = 110

# Màu nền / chữ theo trạng thái thẻ.
_HIDDEN_BG = "#37474F"
_CRIMINAL_BG = "#B71C1C"
_INNOCENT_BG = "#1B5E20"
_TEXT_COLOR = "#FFFFFF"
_HIGHLIGHT_BORDER = "#FFC107"
_HINT_BORDER = "#29B6F6"
_NORMAL_BORDER = "#78909C"


class BoardView(QWidget):
    """Widget hiển thị lưới bàn cờ và nhân vật."""

    cell_submitted = pyqtSignal(str, object)  # (coord, Status)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.grid_layout = QGridLayout(self)
        self.grid_layout.setSpacing(6)
        self._cell_widgets: dict[Coord, QPushButton] = {}
        self._header_widgets: list[QLabel] = []
        self._cells: dict[Coord, PublicCell] = {}
        self._size = 0
        self._highlighted_cells: set[Coord] = set()
        self._hint_cell: Coord | None = None
        self._input_enabled = True
        self._animations: dict[Coord, QVariantAnimation] = {}

    # ------------------------------------------------------------------ API
    def update_board(self, state: PublicState) -> None:
        """Cập nhật toàn bộ giao diện lưới theo PublicState mới."""
        if state.size != self._size or not self._cell_widgets:
            self._rebuild(state)
            return

        for cell in state.cells:
            old = self._cells.get(cell.coord)
            self._cells[cell.coord] = cell
            button = self._cell_widgets[cell.coord]
            if old is not None and not old.revealed and cell.revealed:
                self._flip(cell.coord, button)
            else:
                self._cancel_animation(cell.coord)
                self._apply_card(button, cell)

    def highlight_cells(self, coords: tuple[Coord, ...]) -> None:
        """Highlight viền màu nổi bật cho các ô có trong coords."""
        self._highlighted_cells = set(coords)
        self._restyle_all()

    def clear_highlights(self) -> None:
        """Xóa toàn bộ hiệu ứng highlight (kể cả ô gợi ý)."""
        self._highlighted_cells.clear()
        self._hint_cell = None
        self._restyle_all()

    def mark_hint(self, coord: Coord | None) -> None:
        """Đánh dấu ô được gợi ý bằng viền màu khác với highlight của clue."""
        self._hint_cell = coord
        self._restyle_all()

    def set_input_enabled(self, enabled: bool) -> None:
        """Cho phép hoặc chặn người chơi click ô (chặn khi Auto Solve đang chạy)."""
        self._input_enabled = enabled

    # ------------------------------------------------------------ internals
    def _rebuild(self, state: PublicState) -> None:
        """Xóa và dựng lại toàn bộ lưới (khi nạp puzzle mới hoặc đổi kích thước)."""
        for anim in self._animations.values():
            anim.stop()
        self._animations.clear()
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
        self._cell_widgets.clear()
        self._header_widgets.clear()
        self._cells.clear()
        self._highlighted_cells.clear()
        self._hint_cell = None
        self._size = state.size

        for i in range(state.size):
            col_label = self._make_header(chr(ord("A") + i))
            row_label = self._make_header(str(i + 1))
            self.grid_layout.addWidget(col_label, 0, i + 1)
            self.grid_layout.addWidget(row_label, i + 1, 0)

        for cell in state.cells:
            col, row = parse_coord(cell.coord)
            button = QPushButton(self)
            button.setMinimumSize(CARD_MIN_WIDTH, CARD_MIN_HEIGHT)
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.clicked.connect(lambda _checked=False, c=cell.coord: self._on_card_clicked(c))
            self._cell_widgets[cell.coord] = button
            self._cells[cell.coord] = cell
            self.grid_layout.addWidget(button, row + 1, col + 1)
            self._apply_card(button, cell)

    def _make_header(self, text: str) -> QLabel:
        label = QLabel(f"<b>{text}</b>", self)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._header_widgets.append(label)
        return label

    def _card_text(self, cell: PublicCell) -> str:
        if not cell.revealed:
            status_line = "? ÚP ?"
        elif cell.status == Status.CRIMINAL:
            status_line = "CRIMINAL"
        elif cell.status == Status.INNOCENT:
            status_line = "INNOCENT"
        else:
            status_line = ""
        return f"{cell.coord}\n{cell.name}\n{cell.job}\n{status_line}"

    def _card_background(self, cell: PublicCell) -> str:
        if not cell.revealed:
            return _HIDDEN_BG
        if cell.status == Status.CRIMINAL:
            return _CRIMINAL_BG
        if cell.status == Status.INNOCENT:
            return _INNOCENT_BG
        return _HIDDEN_BG

    def _style_for(self, cell: PublicCell) -> str:
        """Sinh QSS cho một thẻ, có tính đến highlight clue và ô gợi ý."""
        if cell.coord == self._hint_cell:
            border = f"4px solid {_HINT_BORDER}"
        elif cell.coord in self._highlighted_cells:
            border = f"4px solid {_HIGHLIGHT_BORDER}"
        else:
            border = f"2px solid {_NORMAL_BORDER}"
        return (
            f"QPushButton {{ background-color: {self._card_background(cell)};"
            f" color: {_TEXT_COLOR}; border: {border}; border-radius: 8px;"
            f" font-size: 13px; padding: 4px; }}"
            f"QPushButton:hover {{ border-color: #FFFFFF; }}"
        )

    def _apply_card(self, button: QPushButton, cell: PublicCell) -> None:
        button.setText(self._card_text(cell))
        button.setStyleSheet(self._style_for(cell))
        button.setMinimumWidth(CARD_MIN_WIDTH)
        button.setMaximumWidth(16777215)

    def _restyle_all(self) -> None:
        for coord, button in self._cell_widgets.items():
            if coord in self._animations:
                continue  # đang lật, sẽ tự áp style khi xong
            button.setStyleSheet(self._style_for(self._cells[coord]))

    def _cancel_animation(self, coord: Coord) -> None:
        anim = self._animations.pop(coord, None)
        if anim is not None:
            anim.stop()

    def _flip(self, coord: Coord, button: QPushButton) -> None:
        """Hiệu ứng lật thẻ: thu hẹp bề rộng về 0, đổi mặt, rồi nở ra lại."""
        self._cancel_animation(coord)
        full_width = max(button.width(), CARD_MIN_WIDTH)
        button.setMinimumWidth(0)
        anim = QVariantAnimation(self)
        anim.setDuration(FLIP_HALF_MS)
        anim.setStartValue(full_width)
        anim.setEndValue(0)
        self._animations[coord] = anim

        def on_value(value: object) -> None:
            button.setMaximumWidth(int(value))

        def on_shrunk() -> None:
            # Mặt sau (đã lật) hiện ra, sau đó nở lại.
            button.setText(self._card_text(self._cells[coord]))
            button.setStyleSheet(self._style_for(self._cells[coord]))
            grow = QVariantAnimation(self)
            grow.setDuration(FLIP_HALF_MS)
            grow.setStartValue(0)
            grow.setEndValue(full_width)
            grow.valueChanged.connect(on_value)
            grow.finished.connect(on_grown)
            self._animations[coord] = grow
            grow.start()

        def on_grown() -> None:
            self._animations.pop(coord, None)
            self._apply_card(button, self._cells[coord])

        anim.valueChanged.connect(on_value)
        anim.finished.connect(on_shrunk)
        anim.start()

    def _on_card_clicked(self, coord: Coord) -> None:
        """Click vào thẻ: hỏi CRIMINAL/INNOCENT rồi phát tín hiệu cell_submitted."""
        if not self._input_enabled:
            return
        cell = self._cells.get(coord)
        if cell is None:
            return
        menu = QMenu(self)
        menu.setTitle(f"Ô {coord}: {cell.name}")
        title = menu.addAction(f"Kết luận về {cell.name} ({coord})")
        title.setEnabled(False)
        menu.addSeparator()
        criminal = menu.addAction("🔴 CRIMINAL (tội phạm)")
        innocent = menu.addAction("🟢 INNOCENT (vô tội)")
        chosen = menu.exec(QCursor.pos())
        if chosen is criminal:
            self.cell_submitted.emit(coord, Status.CRIMINAL)
        elif chosen is innocent:
            self.cell_submitted.emit(coord, Status.INNOCENT)
